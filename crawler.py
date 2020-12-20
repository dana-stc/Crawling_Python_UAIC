import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import smtplib  # for email sending function
from email.message import EmailMessage
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


def saveInitialPage(url, name):
    logging.info("Saving a new page to the database")
    collection = connectToMongoDB()

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    website_html = {
        "name": name,
        "HTML": soup.prettify(),
        "newHTML": ''
    }
    # Insert Data
    collection.insert_one(website_html)
    logging.info("Row inserted successfully")


def saveUpdatedHTML(url, name):
    logging.info("Updating newHTML with the latest version...")
    collection = connectToMongoDB()

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    for doc1 in collection.find():
        collection.update_one({"name": name}, {"$set": {"newHTML": soup.prettify()}})
    logging.info("newHTML row updated successfully")


def updateInitialPage(name):
    logging.info("Started updating initial page with its latest version ...")
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


def index(url, name):
    logging.info("Started to look for updates on your page...")
    while True:
        saveUpdatedHTML(url, name)
        time.sleep(5)
        print('5 seconds passed')
        verifyForUpdates(name)
        updateInitialPage(name)


def startTheApp():
    print('Welcome to the most awesome crawler!')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Please select an action you want to perform:')
    print('1. Create a new alert')
    print('2. Update an existing alert')
    print('3. Delete an existing alert')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Please enter the name of the page you want to be notified about!')
    print('-------------------------------------------------------')
    print('Please enter the link of the page you want to be notified about!')
    print('-------------------------------------------------------')
    print('Please enter your email: ')


# saveInitialPage('https://www.instagram.com/ioanastoica/', 'Insta')
index('https://www.ziaruldeiasi.ro/stiri/local', 'Ziarul de Iasi')


def sendEmail():
    senderEmail = 'ioanadana97@gmail.com'
    subject = 'Awesome Crawler'
    receiverEmail = 'ioanadana97@gmail.com'
    password = 'nlnxuhhbckwnpxqi'
    message = 'Subject:{}\n\nHey, this was send using Python.'.format(subject)
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(senderEmail, password)
    print("Login success")
    s.sendmail(senderEmail, receiverEmail, message)
    print("Email has been send to " + receiverEmail)

# sendEmail()
