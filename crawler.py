import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def connectToMongoDB():
    try:
        client = MongoClient(
            'mongodb+srv://ioana:ioana@cluster0.peu1n.mongodb.net/pythonUAIC?retryWrites=true&w=majority')
        logging.info("Connected successfully")
    except:
        logging.error("Could not connect to MongoDB")
    db = client.pythonUAIC
    collection = db.crawler
    return collection


def saveInitialPage():
    logging.info("Calling function saveInitialPage")
    collection = connectToMongoDB()

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    url = "https://www.ziaruldeiasi.ro/stiri/local"
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    # print(soup.prettify())

    website_html = {
        "name": "Ziarul de Iasi",
        "HTML": soup.prettify(),
        "newHTML": ''
    }
    # Insert Data
    rec_id1 = collection.insert_one(website_html)
    logging.info("Row inserted successfully")


def saveUpdatedHTML(name):
    logging.info("Started to look for updates on your page...")
    collection = connectToMongoDB()

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    url = "https://www.ziaruldeiasi.ro/stiri/local"
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    for doc1 in collection.find():
        collection.update_one({"name": name}, {"$set": {"newHTML": soup.prettify()}})
    logging.info("newHTML row updated successfully")


def updateInitialPage(name):
    logging.info("Calling function updateInitialPage")
    collection = connectToMongoDB()

    for doc in list(collection.find({"name": name})):
        newHTML = doc["newHTML"]

    for doc1 in collection.find():
        collection.update_one({"name": name}, {"$set": {"HTML": newHTML}})
    logging.info("Updated old HTML with newHTML")


def verifyForUpdates(name):
    logging.info("Started verifying initial HTML with newHTML ...")
    collection = connectToMongoDB()

    documents = list(collection.find({"name": name}))
    for doc in documents:
        HTML = doc["HTML"]
        updatedHTML = doc["newHTML"]
        if HTML == updatedHTML:
            print("same page")
        else:
            print("different")


def index(name):
    while True:
        saveUpdatedHTML(name)
        time.sleep(5)
        print('5 seconds passed')
        verifyForUpdates(name)
        updateInitialPage(name)


index('Ziarul de Iasi')
