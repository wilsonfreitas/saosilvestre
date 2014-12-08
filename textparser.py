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
        self.parsers = self.__createMethodAnalyzers()
        
    def __createMethodAnalyzers(self):
        pairs = []
        for methodName in dir(self):
            method = getattr(self, methodName)
            if methodName.startswith('parse') and type(method) is MethodType and method.__doc__:
                pairs.append(buildparser(method.__doc__, method))
        return pairs
    
    def parse(self, text):
        for parser in self.parsers:
            val = parser(text)
            if val != text:
                return val
        return self.parseText(text)
    
    def parseText(self, text):
        return text


class BooleanParser(TextParser):
    def parseBoolean(self, text, match):
        r'^[Tt][Rr][Uu][eE]|[Ff][Aa][Ll][Ss][Ee]$'
        return eval(text.lower().capitalize())
    
    def parseBoolean_ptBR(self, text, match):
        r'^(sim|Sim|SIM|n.o|N.o|N.O)$'
        return text[0].lower() == 's'


class NumberParser(TextParser):
    def parseInteger(self, text, match):
        r'^-?\s*\d+$'
        return eval(text)
    
    def parse_number_decimal(self, text, match):
        r'^-?\s*\d+[\.,]\d+?$'
        text = text.replace(',', '.')
        return eval(text)
    
    def parse_number_with_thousands(self, text, match):
        r'^-?\s*(\d+[,])+\d+[\.]\d+?$'
        text = text.replace(',', '')
        return eval(text)
    
    def parse_number_with_thousands_ptBR(self, text, match):
        r'^-?\s*(\d+[\.])+\d+[,]\d+?$'
        text = text.replace('.', '')
        text = text.replace(',', '.')
        return eval(text)


def textparse(text, regex, func):
    parser = buildparser(regex, func)
    return parser(text)


def buildparser(regex, func):
    _regex = re.compile(regex)
    def _func(text):
        match = _regex.match(text)
        return func(text, match) if match else text
    return _func


class MegaParser(NumberParser, BooleanParser):
    pass


parser = MegaParser()
parse = parser.parse


if __name__ == '__main__':
    parser = MegaParser()
    assert parser.parse('1.1') == 1.1
    assert parser.parse('1,1') == 1.1
    assert parser.parse('-1,1') == -1.1
    assert parser.parse('- 1,1') == -1.1
    assert parser.parse('11') == 11
    assert parser.parse('true')
    assert parser.parse('Wálson') == 'Wálson'
    assert parser.parse('1.100,01') == 1100.01
    assert parser.parse('1,100.01') == 1100.01
    assert textparse('TRUe', r'^[Tt][Rr][Uu][eE]|[Ff][Aa][Ll][Ss][Ee]$', lambda t, m: eval(t.lower().capitalize()))
    assert textparse('1,1', r'^-?\s*\d+[\.,]\d+?$', lambda t, m: eval(t.replace(',', '.'))) == 1.1
    num_parser = buildparser(r'^-?\s*\d+[\.,]\d+?$', lambda t, m: eval(t.replace(',', '.')))
    assert num_parser('1,1') == 1.1
    
    