import requests as rq
from bs4 import BeautifulSoup
import time
from datetime import datetime
from dateutil import parser
from newspaper import Article
import concurrent.futures
from datetime import datetime
import pysolr

import os 

solrLinks = pysolr.Solr('http://192.168.1.7:8983/solr/links/', timeout=10)
solrNoticias = pysolr.Solr('http://192.168.1.7:8983/solr/noticias/', timeout=10)


quantThreads = 5



def selectSolr(solr):
    results = solr.search('capturada:false',rows=1000)
    return list(results)


def insertSolr(solr,document):
    solr.add([document])

def Thread(works,increase_function,quantThreads):
    start = datetime.now()
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=quantThreads)
    (pool.map(increase_function,works))
    end = datetime.now()
    print("Took {}s to increase the prices with python Threads".format((end - start).total_seconds()))

def insertNuvem(json):  
    try:
        dicio = {"url":json['url']}
        element = collection.find_one(dicio) 
        if element is None:
            collection.insert(json)
            print("Nova Notícia")
            print(json)
        else:
            json['data_captura'] = element['data_captura']
            json['print'] = element['print']
            json['analise'] = element['analise']
            collection.update(dicio,json)
            print("Atualizado")
    except Exception as ex :
        print(ex)

def getLinkNoticia(element,configs):
    links =  []
    for config in configs['linkNoticia']:
        links = links  + (element.find_all(config['tag'],{'class': config['class']}))
    return links

def getTitulo(element,config):
    try:
        return element.find(config['titulo']['tag'],{'class':config['titulo']['class']}).text
    except:
        return '' 
def getSubTitulo(element,config):
    try:
        return element.find(config['subTitulo']['tag'],{'class':config['subTitulo']['class']}).text
    except:
        return ''
def getAutor(element,config):
    try:
        return element.find(config['autor']['tag'],class_=config['autor']['class']).text
    except:
        return ''
def getData(element,config):
    try:
        return parser.parse(element.find(config['data']['tag']).text)
    except:
        return ''
def getDate(element):
    try:
        return element.date()
    except:
        return ''
def getHora(element):
    try:
        return element.time()

    except:
        return ''
def removeLinks(links,urlBase):
    resultLinks = []
    lenBase = len(urlBase)
    for link in links:
        if(link[0:lenBase].find(urlBase) != -1):
            resultLinks.append(link)
    return resultLinks 


def getTexto(element,config):
    try:
        text = element.find(config['corpoNoticia']['tag'],class_=config['corpoNoticia']['class']).find_all(config['texto']['tag'],{'class': config['texto']['class']})
        texto = ''
        for p in text:
            texto = texto + p.text
        return texto
    except Exception as ex:
        print(ex)
        return ''

  
def captureNewsPapper(link):
    try:
        url = link['id'].replace('whatsapp://send?text=','')
        toi_article = Article(url)

        toi_article.download() 
        toi_article.parse() 
        data = toi_article.publish_date

        elemento = {
                'veiculo': link['veiculo'],
                'idveiculo':link['id_veiculo'],
                'url':url,
                'titulo':toi_article.title,
                'resumo':toi_article.summary,
                'texto': BeautifulSoup(toi_article.text, 'html.parser').text,
                'autor': toi_article.authors,
                'data_completa':data,
                #'data': getDate(data),
                #'hora': getHora(data),
                'data_captura': datetime.now(),                    
                'categoria': None,
                'analise':None,
                'print': False,
                'imagem': False,
                'tiragem':link['tiragem'],


        }
        if elemento['texto'] != '':
            insertSolr(solrNoticias,elemento)
    except Exception as ex:
      print(ex)
      print("inserindo com erro")
      link['capturada'] = True
      insertSolr(solrLinks,link)
    finally:
      link['capturada'] = True
      insertSolr(solrLinks,link)


try:
    links = selectSolr(solrLinks)
    print(len(links))
    Thread(links,captureNewsPapper,quantThreads)
except Exception as ex:
    print(ex)

