import scrapy

from tutorial.DAO.ConnectionDB import ConnectionDB


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    connectionDB = ConnectionDB()
    start_urls = connectionDB.findLinks(0,10)

    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, meta={
                'splash': {
                    'endpoint': 'render.html',
                    'args': {'wait': 4}
                }
            })




    def parse(self, response):
        json = {'_id':response.url,'html': str(response.body)}
        self.connectionDB.insertOrUpdate(json)