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
                yield scrapy.Request(url, callback=self.parse)

    def getLink(self,selector,urlVeiculo):
        try:
            link = selector.xpath("@href").extract_first()
            if link is not None:
                if link.find('http') == -1 :
                    if link[0] == '/' and urlVeiculo[-1] == '/':
                        return urlVeiculo + link[1:]
                    elif link[0] != '/' and urlVeiculo[-1] == '/':
                        return urlVeiculo + link
                    elif urlVeiculo[-1] != '/' and link[0] != '/':
                        return urlVeiculo + '/' + link

                return link
            else:
                return ''
        except:
            return ''



    def parse(self, response):
        a_selectors = response.xpath("//a")
        links = []
        veiculo = self.connectionDB.selectVeiculoURL(response.url)
        for selector in a_selectors:
            if self.getLink(selector, veiculo[3]).find(veiculo[3]) != -1:
                json = {
                    "id": self.getLink(selector, veiculo[3]),
                    "url_capturada":  self.getLink(selector, veiculo[3]),
                    "capturada": False,
                    "veiculo": veiculo[1],
                    "url_veiculo": veiculo[3],
                    "id_veiculo": veiculo[0],
                    "tiragem": veiculo[2],
                    "data captura": datetime.now(),
                    "lida": False,
                }
                links.append(json)
                print(json['url_veiculo'])
                print(json['url_capturada'])

        self.connectionDB.insertSolr(links)