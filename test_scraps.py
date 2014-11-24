from mock import Mock
import unittest
import scraps

class TestScrap(unittest.TestCase):
    def test_Scrap(self):
        """it should create and instanciate a Scrap class"""
        class MyScrap(scraps.Scrap):
            a1 = scraps.Attribute()
        
        myScrap = MyScrap()
        self.assertEquals(myScrap.a1, None)
        
        myScrap.a1 = 1
        self.assertEquals(myScrap.a1, 1)
        
        del(myScrap.a1)
        self.assertEquals(myScrap.a1, None)
    
    def test_Scrap_instanciation(self):
        """it should instanciate a Scrap passing parameter."""
        class MyScrap(scraps.Scrap):
            title = scraps.Attribute()
        myScrap = MyScrap(title='Normstron')
        self.assertEquals(myScrap.title, 'Normstron')
        
    def test_Scrap_instanciation2(self):
        """it should instanciate a Scrap passing an invalid parameter."""
        class MyScrap(scraps.Scrap):
            title = scraps.Attribute()
        with self.assertRaises(Exception):
            myScrap = MyScrap(title1='Normstron')
            
    def test_Scrap_errorisnone(self):
        """it should instanciate a Scrap passing an invalid parameter."""
        class MyScrap(scraps.Scrap):
            float_attr = scraps.FloatAttr()
            _error_is_none = True
        myScrap = MyScrap(float_attr='--')
        self.assertEquals(myScrap.float_attr, None)
        # ---
        class MyScrap(scraps.Scrap):
            float_attr = scraps.FloatAttr()
        with self.assertRaises(Exception):
            myScrap = MyScrap(float_attr='--')

class TestAttribute(unittest.TestCase):
    def setUp(self):
        class Obj(object):
            attrs = {}
        self.obj = Obj()
    def test_Attribute(self):
        """    it should instanciate an Attribute class and its descriptor 
            methods
        """
        a = scraps.Attribute()
        self.assertEquals(a.__get__(self.obj), None)
        a.__set__(self.obj, 1)
        self.assertEquals(a.__get__(self.obj), 1)
        a.__delete__(self.obj)
        self.assertEquals(a.__get__(self.obj), None)
        
    def test_Attribute_repeat(self):
        """it should instanciate a repeated Attribute"""
        a = scraps.Attribute(repeat=True)
        a.__set__(self.obj, 1)
        a.__set__(self.obj, 2)
        self.assertEquals(a.__get__(self.obj), [1,2])
    
    def test_Attribute_transform(self):
        """    it should instanciate an Attribute that should be transformed by some
            function while is set
        """
        a = scraps.Attribute(transform=lambda x: x*100)
        a.__set__(self.obj, 1)
        self.assertEquals(a.__get__(self.obj), 100)
    
class TestFloatAttr(TestAttribute):
    def test_FloatAttr(self):
        """it should instanciate the FloatAttr class and set it with a valid string."""
        a = scraps.FloatAttr()
        a.__set__(self.obj, '2.2')
        self.assertAlmostEqual(a.__get__(self.obj), 2.2)
        
    def test_FloatAttr_int(self):
        """it should instanciate the FloatAttr class and set it with an int."""
        a = scraps.FloatAttr()
        a.__set__(self.obj, 2)
        self.assertAlmostEqual(a.__get__(self.obj), 2.0)

    def test_FloatAttr_float(self):
        """it should instanciate the FloatAttr class and set it with a float."""
        a = scraps.FloatAttr()
        a.__set__(self.obj, 2.2)
        self.assertAlmostEqual(a.__get__(self.obj), 2.2)

    def test_FloatAttr_decimal(self):
        """it should instanciate the FloatAttr class and set it with a decimal."""
        from decimal import Decimal
        a = scraps.FloatAttr()
        a.__set__(self.obj, Decimal(2.2))
        self.assertAlmostEqual(a.__get__(self.obj), 2.2)
        
    def test_FloatAttr_comma(self):
        """    it should instanciate the FloatAttr class and set it with a string
            which represents a float but uses comma as decimal separator."""
        a = scraps.FloatAttr(decimalsep=',')
        a.__set__(self.obj, '2,2')
        self.assertAlmostEqual(a.__get__(self.obj), 2.2)
    
    def test_FloatAttr_percentage(self):
        """    it should instanciate the FloatAttr class and set it with a string
            which represents a percentage, ie, a float followed by the symbol '%'."""
        a = scraps.FloatAttr(percentage=True)
        a.__set__(self.obj, '22 %')
        self.assertAlmostEqual(a.__get__(self.obj), 22./100)
    
    def test_FloatAttr_percentage_comma(self):
        """    it should instanciate the FloatAttr class and set it with a string
            which represents a percentage and uses comma as decimal separator."""
        a = scraps.FloatAttr(decimalsep=',', percentage=True)
        a.__set__(self.obj, '22,5 %')
        self.assertAlmostEqual(a.__get__(self.obj), 22.5/100)

    def test_FloatAttr_thousand(self):
        """    it should instanciate the FloatAttr class and set it with a string
            which represents a float with thousand separators."""
        a = scraps.FloatAttr(thousandsep=',')
        a.__set__(self.obj, '2,222.22')
        self.assertAlmostEqual(a.__get__(self.obj), 2222.22)
        a = scraps.FloatAttr(thousandsep='.', decimalsep=',')
        a.__set__(self.obj, '2.222,22')
        self.assertAlmostEqual(a.__get__(self.obj), 2222.22)
    
    def test_FloatAttr_repeat(self):
        """    it should instanciate the FloatAttr class and set the repeat parameter
            from Attribute."""
        a = scraps.FloatAttr(repeat=True)
        a.__set__(self.obj, '22.5')
        a.__set__(self.obj, '22.5')
        self.assertEquals(a.__get__(self.obj), [22.5, 22.5])
        
    def test_FloatAttr_error(self):
        """    it should instanciate the FloatAttr class with an invalid string."""
        a = scraps.FloatAttr()
        with self.assertRaises(Exception):
            a.__set__(self.obj, '--')
        
    
class TestDatetimeAttr(TestAttribute):
    def test_DatetimeAttr(self):
        """    it should instanciate the DatetimeAttr class and set it with a 
            valid string."""
        from datetime import datetime
        a = scraps.DatetimeAttr(formatstr='%Y-%m-%d %H:%M:%S')
        a.__set__(self.obj, '2013-01-01 15:22:54')
        self.assertEquals(a.__get__(self.obj), datetime(2013, 1, 1, 15, 22, 54))
        
    def test_DatetimeAttr_locale(self):
        """    it should instanciate the DatetimeAttr class and set it with a 
            valid string and locale."""
        from datetime import datetime
        a = scraps.DatetimeAttr(formatstr='%d/%b/%Y', locale='pt_BR')
        a.__set__(self.obj, '11/Dez/2013')
        self.assertEquals(a.__get__(self.obj), datetime(2013, 12, 11))
        # Check if locale have been restored
        a = scraps.DatetimeAttr(formatstr='%d/%b/%Y')
        a.__set__(self.obj, '11/Dec/2013')
        self.assertEquals(a.__get__(self.obj), datetime(2013, 12, 11))

class TestDateAttr(TestAttribute):
    def test_DateAttr(self):
        'it should instanciate the DateAttr class and set it with a valid string.'
        from datetime import datetime
        a = scraps.DateAttr(formatstr='%Y-%m-%d')
        a.__set__(self.obj, '2013-01-01')
        self.assertEquals(a.__get__(self.obj), datetime(2013, 1, 1, 0, 0))
    
    
class TestFetcher(unittest.TestCase):
    def test_Fetcher(self):
        """    it should create a Fetcher."""
        class MyFetcher(scraps.Fetcher):
            url = 'http://httpbin.org/html'
            def parse(self, response):
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text)
                class MockScrap(object):
                    title = soup.html.body.h1.string
                return MockScrap()
        fetcher = MyFetcher()
        ret = fetcher.fetch()
        self.assertEquals(ret.title, 'Herman Melville - Moby-Dick')
        
    def test_Fetcher2(self):
        """    it should create a Fetcher and use a parameterized url."""
        class MyFetcher(scraps.Fetcher):
            url = 'http://httpbin.org/get?name={name}'
            def parse(self, response):
                import json
                ret = json.loads(response.text)
                class MockScrap(object):
                    name = ret['args']['name']
                return MockScrap()
        fetcher = MyFetcher()
        ret = fetcher.fetch(name='freitas')
        self.assertEquals(ret.name, 'freitas')
        
    def test_Fetcher3(self):
        """    it should create a mock Fetcher."""
        fetcher = scraps.Fetcher()
        fetcher.url = 'http://httpbin.org/robots.txt'
        mock_ret = Mock()
        mock_ret.name = 'freitas'
        fetcher.parse = Mock()
        fetcher.parse.return_value = mock_ret
        ret = fetcher.fetch()
        args, kwargs = fetcher.parse.call_args
        self.assertEquals(ret.name, 'freitas')
        self.assertEquals(args[0].code, 200)
        self.assertEquals(args[0].content_type, 'text/plain')
        self.assertEquals(args[0].text, 'User-agent: *\nDisallow: /deny\n')
    

if __name__ == '__main__':
    unittest.main(verbosity=1)

