import constants
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import smtplib
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

    UNALLOWED_TAGS = ['script', 'head']
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    # remove script tags
    for tag in soup.findAll(True):
        if tag.name in UNALLOWED_TAGS:
            tag.extract()
    soup.renderContents()

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

    UNALLOWED_TAGS = ['script']
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    # remove script tags
    for tag in soup.findAll(True):
        if tag.name in UNALLOWED_TAGS:
            tag.hidden = True
    soup.renderContents()

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


def verifyForUpdates(name, rEmail):
    logging.info("Started verifying initial HTML with newHTML ...")
    collection = connectToMongoDB()

    documents = list(collection.find({"name": name}))
    for doc in documents:
        HTML = doc["HTML"]
        updatedHTML = doc["newHTML"]
        if HTML != updatedHTML:
            print("Same")
        else:
            print("The page has changed")
            sendEmail(rEmail, name)


def run(url, name, rEmail):
    logging.info("Started to look for updates on your page...")
    while True:
        saveUpdatedHTML(url, name)
        time.sleep(5)
        print('5 seconds passed')
        verifyForUpdates(name, rEmail)
        updateInitialPage(name)


def sendEmail(email, name):
    logging.info("Started to prepare for sending the email...")
    senderEmail = constants.EMAIL
    password = constants.PASS
    receiverEmail = email
    subject = 'Awesome Crawler'
    message = 'Subject:{}\n\nPagina web ' + name + ' a fost modificata.'.format(subject)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(senderEmail, password)
    logging.info("Login success")
    s.sendmail(senderEmail, receiverEmail, message)
    logging.info("Email has been send to " + receiverEmail)


def deleteSavedPage(name):
    logging.info("Called function deletedSavedPage ...")
    collection = connectToMongoDB()
    myquery = {"name": name}
    collection.delete_one(myquery)


def startTheApp():
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Welcome to the most awesome crawler!')
    option = principalMenu()
    if option == '1':
        createAlert()
    elif option == '2':
        updateAlert()
    elif option == '3':
        deleteAlert()
    else:
        print('Invalid option!')
        startTheApp()


def principalMenu():
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Please select an action you want to perform:')
    print('1. Create a new alert')
    print('2. Update an existing alert')
    print('3. Delete an existing alert')
    option = input('Enter the number of your option here: ')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return option


def createAlert():
    name = input('Please enter the name of the page you want to be notified about: ')
    url = input('Please enter the link of the page you want to be notified about: ')
    mail = input('Please enter your email: ')
    saveInitialPage(url, name)
    run(url, name, mail)
    startTheApp()


def deleteAlert():
    name = input('Please enter the name of the alert you want to delete: ')
    deleteSavedPage(name)
    startTheApp()


startTheApp()

# update and delete functionalities
# name of the changed page in the email
