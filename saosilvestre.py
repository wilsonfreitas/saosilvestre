
import itertools
from functools import partial
import scraps
import textparser
import tinydf

class SaoSilvestreParser(textparser.TextParser):
    def parseNaturalidade(self, text, match):
        r'^Naturalidade:\s(.+)\s?$'
        return ('pais', match.group(1))
    
    def parseHorarioLargada(self, text, match):
        r'^Horário da Largada:\s(\d?\d)h(\d\d)\s?$'
        return ('horario', '{0}:{1}:00'.format(match.group(1), match.group(2)))
    
    def parseHorarioLargada2(self, text, match):
        r'^Horário da Largada:\s(\d+) horas'
        return ('horario', '{0}:00:00'.format(match.group(1)))
    
    def parseTempo(self, text, match):
        r'^Tempo\s?:\s?(\d\d)m(in)?(\d\d)s?'
        return ('tempo', '00:{0}:{1}.000'.format(match.group(1), match.group(3)))
    
    def parsePercurso(self, text, match):
        r'^Percurso:.*\s(\d+(\.\d+)?)\s?([Kk]?)m\s?$'
        return ('percurso', eval(match.group(1).replace('.', '')) * (1000 if match.group(3).lower() == 'k' else 1))
    
    def parseParticipantes(self, text, match):
        r'^Participantes:\s(\d+\.\d+)\satletas\.\s?$'
        return ('participantes', eval(match.group(1).replace('.', '')))
    
    def parseLargada(self, text, match):
        r'Largada:\s(.+)\.?\s?$'
        return ('largada', match.group(1))
    
    def parseChegada(self, text, match):
        r'Chegada:\s(.+)\.?\s?$'
        return ('chegada', match.group(1))
    
    def parseRace(self, text, match):
        r'^(\d+). Corrida de São Silvestre – (\d\d\d\d)a?$'
        return [('corrida', eval(match.group(1))), ('ano', eval(match.group(2)))]
    
    def parseText(self, text):
        return None


def keyfy(seq, key):
    return list(map(lambda x: [(key, x)], seq))


class SaoSilvestreScrap(scraps.Scrap):
    names = scraps.Attribute(xpath='//*[@id="content"]/div/div/div/div/div/h2')
    races = scraps.Attribute(xpath='//*[@id="content"]/div/div/div/div/div/h4')
    info1 = scraps.Attribute(xpath='//*[@id="content"]/div/div/div/div/div/p[1]', apply=[
        partial(str.split, sep='\n'), lambda seq: [str.strip(s) for s in seq]
    ])
    info2 = scraps.Attribute(xpath='//*[@id="content"]/div/div/div/div/div/p[2]', apply=[
        partial(str.split, sep='\n'), lambda seq: [str.strip(s) for s in seq]
    ])


class SaoSilvestrFetcher(scraps.Fetcher):
    scrapclass = SaoSilvestreScrap
    url = 'http://www.saosilvestre.com.br/campeoes/campeoes-{0}-{1}/'


class SaoSilvestrFetcher2(SaoSilvestrFetcher):
    url = 'http://www.saosilvestre.com.br/campeoes/{0}-{1}/'


if __name__ == '__main__':
    parser = SaoSilvestreParser()
    fetcher = SaoSilvestrFetcher()
    fetcher2 = SaoSilvestrFetcher2()
    ds = tinydf.DataFrame()
    ds.headers = ['nome', 'pais', 'corrida', 'ano', 'horario', 'tempo', 'percurso', 'largada', 'chegada']
    decades = [(2010, 2013), (2000, 2009), (1990, 1999), (1980, 1989), (1970, 1979), (1960, 1969), (1950, 1959),
               (1940, 1949), (1930, 1939), (1925, 1929)]
    parse_and_filter_false = scraps.compose(partial(map, parser.parse), partial(filter, lambda x: x is not None), list)
    for dec in decades:
        try:
            res = fetcher.fetch(*dec)
        except:
            res = fetcher2.fetch(*dec)
        info1 = [parse_and_filter_false(x) for x in res.info1]
        info2 = [parse_and_filter_false(x) for x in res.info2]
        races = parse_and_filter_false(res.races)
        names = keyfy(res.names, 'nome')
        rows = [dict(info1 + info2 + race + name) for info1, info2, race, name in zip(info1, info2, races, names)]
        for row in rows:
            ds.add(**row)
    print(ds.csv)
