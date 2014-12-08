
from functools import reduce
import types
from decimal import Decimal
import types
import pprint
import inspect
import urllib.request, urllib.error, urllib.parse
from datetime import datetime
from lxml import html

__all__ = ['Fetcher', 'Scrap', 'Attribute', 'FloatAttr', 'DateAttr', 'DatetimeAttr']

class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, value):
        self[attr] = value
        

def fetch(url, scrap, *args, **kwargs):
    opener = urllib.request.build_opener()
    req = urllib.request.Request(url.format(*args, **kwargs))
    res = opener.open(req)
    response = AttrDict()
    response.text = res.read()
    response.code = res.getcode()
    scrap.lxml_parser(response.text)

class Fetcher(object):
    """    Fetcher class represents the request handler. It defines the URL to be
    requested so as the method to parse.
    """
    def fetch(self, *args, **kwargs):
        opener = urllib.request.build_opener()
        req = urllib.request.Request(self.url.format(*args, **kwargs))
        res = opener.open(req)
        response = AttrDict()
        response.text = res.read()
        response.code = res.getcode()
        # response.date = res.info().getheader('date')
        # response.content_type = res.info().getheader('content-type')
        # response.content_length = res.info().getheader('content-length')
        return self.parse(response)
    
    def parse(self, response):
        scrap = self.scrapclass()
        scrap.lxml_parser(response.text)
        return scrap
    
    # def parse(self, content):
    #     """    it receives the fetched content, parses it and returns a Scrap."""
    #     raise NotImplemented('This method must be inherited.')


class Scrap(object):
    """    Scrap class represents a bunch of data collected from information
        sources.
    """
    def __new__(cls, *args, **kwargs):
        obj = super(Scrap, cls).__new__(cls)
        pairs = [(k,v) for k,v in list(cls.__dict__.items()) if isinstance(v, Attribute)]
        obj.xpaths = {}
        obj.attrs = {}
        for k,v in pairs:
            v.index = k
            obj.xpaths[k] = v.xpath
            obj.attrs[k] = None
        return obj
    
    def __init__(self, **kwargs):
        prop_names = [member[0] for member in inspect.getmembers(self)
            if not member[0].startswith('__')]
        if '_error_is_none' not in prop_names:
            self._error_is_none = False
        for prop_name, prop_value in list(kwargs.items()):
            if prop_name not in prop_names:
                raise KeyError('Invalid attribute: ' + prop_name)
            try:
                setattr(self, prop_name, prop_value)
            except Exception as e:
                if not self._error_is_none:
                    raise e
                    
    def __repr__(self):
        d = {}
        for propname in self.attrs:
            d[propname] = getattr(self, propname)
        return pprint.pformat(d)
    
    __str__ = __repr__
    
    def lxml_parser(self, content):
        doc = html.document_fromstring(content)
        for k, xpath in list(self.xpaths.items()):
            elms = doc.xpath(xpath)
            setattr(self, k, [r.text_content().strip() for r in elms if r.text_content()])


class Attribute(object):
    """    Attribute class is a descriptor which represents each chunk of
        data extracted from a source of information.
    """
    def __init__(self, xpath, apply=[]):
        self.xpath = xpath
        self.index = None
        self.apply = apply
    
    def parse(self, value):
        return value
    
    def __set__(self, obj, value):
        """sets attribute's value"""
        try:
            iter(value)
        except:
            value = [value]
        if len(self.apply) == 0:
            apply = lambda x: x
        else:
            apply = compose(*self.apply)
        value = [apply(self.parse(v)) for v in value]
        obj.attrs[self.index] = value
    
    def __get__(self, obj, typo=None):
        """gets attribute's value"""
        try:
            return obj.attrs[self.index]
        except KeyError:
            return None
        
    def __delete__(self, obj):
        """resets attribute's initial state"""
        obj.attrs[self.index] = None


class FloatAttr(Attribute):
    """    FloatAttr class is an Attribute descriptor which tries to convert to 
        float every value set. It should convert mainly strings though numeric 
        types such as int and decimal could be set.
    """
    def __init__(self, thousandsep=None, decimalsep=None, percentage=False, **kwargs):
        super(FloatAttr, self).__init__(**kwargs)
        self.decimalsep = decimalsep
        self.percentage = percentage
        self.thousandsep = thousandsep
    
    def parse(self, value):
        if type(value) in (str, str):
            if self.thousandsep is not None:
                value = value.replace(self.thousandsep, '')
            if self.decimalsep is not None:
                value = value.replace(self.decimalsep, '.')
            if self.percentage:
                value = value.replace('%', '')
        if self.percentage:
            value = float(value)/100
        else:
            value = float(value)
        return value


class BaseDatetimeAttr(Attribute):
    """    BaseDatetimeAttr class is an Attribute descriptor which parses a string
        using a datetime format string and stores an iso-formated datetime 
        string.
    """
    def __init__(self, formatstr=None, locale=None, **kwargs):
        super(BaseDatetimeAttr, self).__init__(**kwargs)
        self.formatstr = formatstr
        self.locale = locale
        
    def parse(self, value):
        # if self.locale:
        #     import locale
        #     locale.setlocale(locale.LC_TIME, 'pt_BR')
        value = value.replace('Dez', 'Dec')
        value = datetime.strptime(value, self.formatstr)
        # value = value.replace('Dec', 'De')
        # if self.locale:
        #     locale.setlocale(locale.LC_TIME, '')
        return value
        
    
class DatetimeAttr(BaseDatetimeAttr):
    """    DatetimeAttr class is an Attribute descriptor which parses a string 
        using a datetime format string and stores an iso-formated datetime 
        string.
    """
    def parse(self, value):
        value = super(DatetimeAttr, self).parse(value)
        # return value.isoformat()
        return value
        
class DateAttr(BaseDatetimeAttr):
    """    DateAttr class is an Attribute descriptor which parses a string 
        using a datetime format string and stores an iso-formated datetime 
        string.
    """
    def parse(self, value):
        value = super(DateAttr, self).parse(value)
        # return value.date().isoformat()
        return value


def import_func(className, modName=None):
    if not modName:
        fields = className.split('.')
        modName = '.'.join(fields[:-1])
        className = fields[-1]
    if modName is '':
        modName = '__main__'
    module = __import__(modName, globals(), locals(), [className], -1)
    func = getattr(module, className)
    if type(func) is types.ModuleType:
        raise TypeError("Not callable object found")
    else:
        return func


def compose(*functions):
    f = list(functions)
    f.reverse()
    return reduce(lambda f, g: lambda x: f(g(x)), f)


class ProcessFetchers(object):
    def process(self, fetchers):
        for fetcher_config in fetchers:
            # fetcher name: app.fetchers.mod.KlassFetcher
            fetcher_name = fetcher_config['fetcher']
            # import fetcher class
            fetcher_klass = import_func(fetcher_config['fetcher'])
            # instanciate fetcher class
            fetcher = fetcher_klass()
            parms = fetcher_config['parameters']
            # fetch scraps
            scrap = fetcher.fetch(**parms)
            # action name: app.action.mod.KlassAction
            action_name = fetcher_name.replace('Fetcher', 'Action').replace('fetchers', 'action')
            action_klass = import_func(action_name)
            action = action_klass()
            # execute action
            action.execute(scrap)


