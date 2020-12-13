import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


try:
    client = MongoClient('mongodb+srv://ioana:ioana@cluster0.peu1n.mongodb.net/pythonUAIC?retryWrites=true&w=majority')
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

db = client.pythonUAIC
collection = db.crawler

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
    "HTML": soup.prettify()
}

# Insert Data
rec_id1 = collection.insert_one(website_html)
print("Data inserted with record ids", rec_id1)

# Printing the data inserted
cursor = collection.find()
for record in cursor:
    print(record)
