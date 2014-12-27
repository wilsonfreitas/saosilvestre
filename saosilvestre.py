
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


keyfy = lambda seq, key: list(map(lambda x: [(key, x)], seq))


split = lambda sep=None, maxsplit=-1: lambda s: str.split(s, sep=sep, maxsplit=maxsplit)


foreach = lambda func: lambda seq: [func(x) for x in seq]


class SaoSilvestreScrap(scraps.Scrap):
    names = scraps.Attribute(xpath='//*[@id="content"]/div/div/div/div/div/h2')
    races = scraps.Attribute(xpath='//*[@id="content"]/div/div/div/div/div/h4')
    info1 = scraps.Attribute(xpath='//*[@id="content"]/div/div/div/div/div/p[1]', apply=[
        split(sep='\n'), foreach(str.strip)
    ])
    info2 = scraps.Attribute(xpath='//*[@id="content"]/div/div/div/div/div/p[2]', apply=[
        split(sep='\n'), foreach(str.strip)
    ])


if __name__ == '__main__':
    ds = tinydf.DataFrame()
    ds.headers = ['nome', 'pais', 'corrida', 'ano', 'horario', 'tempo', 'percurso', 'largada', 'chegada']
    parser = SaoSilvestreParser()
    parse_and_filter_false = scraps.compose(partial(map, parser.parse), partial(filter, lambda x: x is not None), list)
    decades = [(2010, 2013), (2000, 2009), (1990, 1999), (1980, 1989), (1970, 1979), (1960, 1969), (1950, 1959),
               (1940, 1949), (1930, 1939), (1925, 1929)]
    scrap = SaoSilvestreScrap()
    for dec in decades:
        try:
            scrap.fetch('http://www.saosilvestre.com.br/campeoes/campeoes-{0}-{1}/', *dec)
        except:
            scrap.fetch('http://www.saosilvestre.com.br/campeoes/{0}-{1}/', *dec)
        infos1 = [parse_and_filter_false(x) for x in scrap.info1]
        infos2 = [parse_and_filter_false(x) for x in scrap.info2]
        races = parse_and_filter_false(scrap.races)
        names = keyfy(scrap.names, 'nome')
        rows = [dict(info1 + info2 + race + name) for info1, info2, race, name in zip(infos1, infos2, races, names)]
        for row in rows:
            ds.add(**row)
    print(ds.csv)

