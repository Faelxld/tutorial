import pymysql.cursors
from urllib import request
import requests
import json


import pysolr


class ConnectionDB(object):

    def __init__(self):
      self.connection = self.getConnection()
      self.solr = pysolr.Solr('http://localhost:8983/solr/links/', timeout=10)






    def getConnection(self):
        try:
            connection = pymysql.connect(host='sisiclipping.c9iphzxvhtzw.sa-east-1.rds.amazonaws.com',
                                         user='admin',
                                         password='admdata2708',
                                         db='iclipping',
                                         port=3306)
            print(connection)
            return connection
        except Exception as ex:
            print('Erro Conexão')
            print(ex)

    def selectVeiculos(self, page):
        tamPage = 1000
        offset = (page) * tamPage
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "select id, nome, tier, endereco_internet from veiculos where tipo_veiculo in (7,6,5) AND ativo = 1 Limit " + str(offset) + ',' + str(tamPage)
            cursor.execute(sql)
            result = cursor.fetchall()
        return (result)

    def selectVeiculoURL(self, url):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "select id, nome, tier, endereco_internet from veiculos where  endereco_internet like" + "'%" + str(url) + "%'"
            cursor.execute(sql)
            result = cursor.fetchone()
        return (result)

    def countVeiculos(self):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "select count(nome) from veiculos where tipo_veiculo in (7,6,5) AND ativo = 1 " # AND tier = 1

            cursor.execute(sql)
            result = cursor.fetchone()
        return (result[0])

    def selectSolr(self):
        select = request.urlopen(
            'http://localhost:8983/solr/mycol1/select?q=*%3A*')  # mudar para apenas quem não foi lido
        rsp = json.load(select)
        return rsp


    def insertSolr(self,documents):
        self.solr.add(documents)