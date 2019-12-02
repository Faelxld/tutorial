import scrapy

from tutorial.DAO.ConnectionDB import ConnectionDB


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    connectionDB = ConnectionDB()
    start_urls  = connectionDB.findLinks(0,1000)

    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, meta={
                'splash': {
                    'endpoint': 'render.html',
                    'args': {'wait': 0.5}
                }
            })


    def start_requests2(self):
        const = 1000
        count = self.connectionDB.countOrganizations()
        for i in list(range(0,count,const)):
            self.start_urls = self.connectionDB.findLinks(i,const)
            for url in self.start_urls:
                yield scrapy.Request(url, self.parse, meta={
                    'splash': {
                        'endpoint': 'render.html',
                        'args': {'wait': 7.0}
                    }
                })

    def parse(self, response):
        json = {'html':response.body}
        self.connectionDB.pages.insert_one(json)