from pymongo import MongoClient

class ConnectionDB(object):

    def __init__(self):
        _client = MongoClient('localhost', 27017)
        self.db = _client['bex']
        self.organizations = self.db['organizations']
        self.pages = self.db['pages']

    def insertOrUpdate(self,json):
        try:
            dicio = {"_id": json['_id']}
            element = self.pages.find_one(dicio)
            if element is None:
                self.pages.insert(json)
            else:
                self.pages.update(dicio, json)
        except Exception as ex:
            print(ex)
    def formatLink(self,link):
        limit = link.find('?')
        return link[0:limit-1] + '/'
    def findLinks(self,pageInicial,const):
        elements = list(self.organizations.find({'lido': False}).skip(pageInicial).limit(pageInicial+const))
        lista = []
        for element in elements:
            lista.append((element['crunchbase_url']))
        return lista
    def countOrganizations(self):
        return self.organizations.count()
