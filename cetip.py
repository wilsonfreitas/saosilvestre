
import scraps
from datetime import datetime


# criar formas funcionais para as funções python
# pex.
# str.replace(x, from, to) --> replace(from, to)(x)
# str.lower(x) --> lower()(x) ou lower...(x)


def strptime(format='%Y-%m-%d'):
    return lambda text: datetime.strptime(text, format)


foreach = lambda func: lambda seq: [func(x) for x in seq]


def _nothing():
    while True:
        yield ''

nothing = _nothing()

def replace(_from, _to):
    def _replace(text):
        for f, t in zip(_from, _to):
            text = text.replace(f, t)
        return text
    return _replace


divide_by = lambda x: lambda y: y/x


class CetipScrap(scraps.Scrap):
    data = scraps.Attribute(xpath='//*[@id="ctl00_Banner_lblTaxDateDI"]', apply=[
        replace(')(', nothing), strptime('%d/%m/%Y')
    ])
    taxa = scraps.Attribute(xpath='//*[@id="ctl00_Banner_lblTaxDI"]', apply=[
        replace(',%', ['.', '']), float, divide_by(100)
    ])


scrap = CetipScrap()
scrap.fetch('http://www.cetip.com.br')

print(scrap.data)
print(scrap.taxa)
