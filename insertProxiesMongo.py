from pymongo import MongoClient 
import json 


client = MongoClient()
db = client["proxies"]
collection = db["proxies"]


def insertOrUpdate(json):       
    try: 
        dicio = {"_id":json['_id']} 
        if collection.find_one(dicio) is None:
            collection.insert(json)
            print(json)
        else:
            collection.update(dicio,json)
            print("Atualizado")     
    except Exception as ex :
        print(ex)

jsons = json.load(open('proxys.json'))


for element in jsons:
    insertOrUpdate({'_id':element['ip'],'proxy':element['proxy'],'speed':element['speed']})