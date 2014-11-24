# encoding: utf-8

import re
from types import MethodType

class TextParser(object):
    """
    Generic parser applied to column fields of a statements block.
    The methods used to parse column fields start with parse and receives two parameters:
    text to be parsed and match object of re module.
    """
    def __init__(self):
        self.regexes = self.__createMethodAnalyzers()
        
    def __createMethodAnalyzers(self):
        pairs = []
        for methodName in dir(self):
            method = getattr(self, methodName)
            if methodName.startswith('parse') and type(method) is MethodType and method.__doc__:
                pairs.append( (re.compile(method.__doc__), method) )
        return pairs
    
    def parse(self, text):
        result = None
        for regex, func in self.regexes:
            match = regex.match(text)
            if match:
                result = func(text, match)
                break
        if result is None:
            result = self.parseText(text)
        return result
    
    def parseInteger(self, text, match):
        r'^-?\s*\d+$'
        return eval(text)
    
    def parseNumber3(self, text, match):
        r'^-?\s*(\d+[,])+\d+[\.]\d+?$'
        text = text.replace(',', '')
        return eval(text)
    
    def parseNumber2(self, text, match):
        r'^-?\s*(\d+[\.])+\d+[,]\d+?$'
        text = text.replace('.', '')
        text = text.replace(',', '.')
        return eval(text)
    
    def parseNumber(self, text, match):
        r'^-?\s*\d+[\.,]\d+?$'
        text = text.replace(',', '.')
        return eval(text)
    
    def parseBoolean(self, text, match):
        r'^[Tt][Rr][Uu][eE]|[Ff][Aa][Ll][Ss][Ee]$'
        return eval(text.lower().capitalize())
    
    def parseBoolean2(self, text, match):
        r'^(sim|Sim|SIM|n.o|N.o|N.O)$'
        return text[0].lower() == 's'
    
    def parseText(self, text):
        return text

parser = TextParser()
parse = parser.parse

if __name__ == '__main__':
    parser = TextParser()
    assert parser.parse('1.1') == 1.1
    assert parser.parse('1,1') == 1.1
    assert parser.parse('11') == 11
    assert parser.parse('true')
    assert parser.parse('Wálson') == 'Wálson'
    assert parser.parse('1.100,01') == 1100.01
    assert parser.parse('1,100.01') == 1100.01
    
    
    