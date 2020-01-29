import scrapy
from datetime import datetime
from tutorial.DAO.ConnectionDB import ConnectionDB


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    connectionDB = ConnectionDB()
    start_urls = []
    url_veiculo = ''
    id_veiculo = ''
    nome_veiculo = ''
    tiragem = ''

    def start_requests(self):

        totalVeiculos = self.connectionDB.countVeiculos()

        for i in list(range(1,totalVeiculos)):
            self.start_urls = self.connectionDB.selectVeiculos(i)
            print('Start ' + str(len(self.start_urls)))
            for veiculo in self.start_urls:
                url = veiculo[3]
                self.url_veiculo = url
                self.id_veiculo = veiculo[0]
                self.nome_veiculo = veiculo[1]
                self.tiragem = veiculo[2]
                yield scrapy.Request(url, callback=self.parse, 
                cb_kwargs=dict(main_id= veiculo[0]),
                meta={
                'splash': {
                    'endpoint': 'render.html',
                    'args': {'wait': 6}
                }
            })



    def  getListaRegex(self):
        return ['twitter.com','facebook.com','instagram.com','youtube.com','youtu.br','linkedin.com']
  
    def getLink(self,selector,urlVeiculo):
        try:
            link = selector.xpath("@href").extract_first().replace('whatsapp://send?text=','')
            for regex in self.getListaRegex():
                if link.find(regex) != -1:
                    return None
            urlBase = urlVeiculo.replace('http://','').replace('https://','')
            if link.find(urlBase) == -1 and link.find('http:') == -1 and link.find('https:')  == -1:
                if link[0] == '/' and urlVeiculo[-1] == '/':
                    return urlVeiculo + link[1:]
                elif link[0] != '/' and urlVeiculo[-1] == '/':
                    return urlVeiculo + link
                elif urlVeiculo[-1] != '/' and link[0] != '/':
                    return urlVeiculo + '/' + link
            elif link.find(urlBase) != -1 and link.find('http:') == -1 and link.find('https:')  == -1 and link[0:3].find('//') != -1:
                return 'http:' + link
            elif link.find(urlBase) != -1 and link.find('http://') == -1 and link.find('https://')  == -1:
                return 'http://' + link

            else:
                return link             


        except:
            return None

        


    def parse(self, response,main_id):

        a_selectors = response.xpath("//a")
        links = []
        date=datetime.now()
        date=str(date).split(".")
        date=date[0]
        veiculo = self.connectionDB.selectVeiculoId(main_id)
        print('\n\n\n Veiculo')
        print(veiculo)
        for selector in a_selectors:
            link = self.getLink(selector, veiculo[3])
            if link is not None:
                json = {
                    "id": self.getLink(selector, veiculo[3]),
                    "url_capturada":  self.getLink(selector, veiculo[3]),
                    "capturada": False,
                    "veiculo": veiculo[1],
                    "url_veiculo": veiculo[3],
                    "id_veiculo": veiculo[0],
                    "tiragem": veiculo[2],
                    "data captura": date,
                    "lido": False,
                }
                links.append(json)
                print(json['url_veiculo'])
                print(json['url_capturada'])

        self.connectionDB.insertSolr(links)