
import json
import csv
import io


class DataFrame(object):
    keys = ('data', 'attributes', 'headers')
    def __init__(self, **kwargs):
        self.headers = list(kwargs.keys())
        self.data = kwargs
        self.attributes = {}
    
    def __setattr__(self, key, value):
        if key in DataFrame.keys:
            self.__dict__[key] = value
        else:
            ref = self.attributes
            ref[key] = value
    
    def __getattr__(self, key):
        if key in DataFrame.keys:
            return self.__dict__[key]
        else:
            ref = self.attributes
            return ref[key]
    
    def add(self, **row):
        for h in self.headers:
            col = self.data.get(h, [])
            col.append(row.get(h))
            self.data[h] = col
    
    @property
    def csv(self):
        buf = io.StringIO()
        writer = csv.writer(buf)
        headers = self.headers + list(self.attributes.keys())
        writer.writerow(headers)
        if self.data:
            n = len(self.data[self.headers[0]])
            for i in range(n):
                row = []
                for h in self.headers:
                    row.append(self.data[h][i])
                for h in list(self.attributes.keys()):
                    row.append(self.attributes[h])
                writer.writerow(row)
        content = buf.getvalue()
        buf.close()
        return content
    
    @property
    def dict(self):
        df_dict = self.attributes.copy()
        if self.data:
            df_dict['data'] = self.data
        return df_dict
    
    @property
    def json(self):
        df_dict = self.attributes.copy()
        if self.data:
            n = len(self.data[self.headers[0]])
            tab = []
            for i in range(n):
                row = {}
                for h in self.headers:
                    row[h] = self.data[h][i]
                tab.append(row)
            if df_dict:
                df_dict['data'] = tab
            else:
                df_dict = tab
        return json.dumps(df_dict)


if __name__ == '__main__':
    df = DataFrame()
    assert df.dict == {}
    
    # 
    df = DataFrame()
    df.attr1 = 1
    assert df.dict == {'attr1': 1}
    
    # 
    data = {
        'key1': list(range(5)),
        'key2': list('a' * 5)
    }
    df = DataFrame(**data)
    df.attr1 = 'attr1'
    
    assert df.dict == {
        'attr1': 'attr1',
        'data': {
            'key1': list(range(5)),
            'key2': list('a' * 5)
        }
    }
    
    # 
    data = {
        '1 key': list(range(5)),
        '2 key': list('a' * 5)
    }
    df = DataFrame(**data)
    df.attr1 = 'attr1'
    df.attr2 = 1
    
    assert df.dict == {
        'attr1': 'attr1',
        'attr2': 1,
        'data': {
            '1 key': list(range(5)),
            '2 key': list('a' * 5)
        }
    }
    
    # print(df.json)
    # print(df.csv)