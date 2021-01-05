import datetime

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


def saveInitialPage(url, name, dbEmail):
    logging.info("Saving a new page to the database")
    collection = connectToMongoDB()

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    website_html = {
        "name": name,
        "HTML": soup.get_text(),
        "newHTML": '',
        "email": dbEmail,
        "url": url
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

    # for doc in collection.find({"name": name}):
    collection.update_one({"name": name}, {"$set": {"newHTML": soup.get_text()}})
    logging.info("newHTML row updated successfully")


def updateInitialPage(name):
    logging.info("Started updating initial page with its latest version ...")
    collection = connectToMongoDB()

    for doc in collection.find({"name": name}):
        collection.update_one({"name": name}, {"$set": {"HTML": doc["newHTML"]}})
    logging.info("HTML row updated successfully")


def verifyForUpdates(name, rEmail):
    logging.info("Started verifying initial HTML with newHTML ...")
    collection = connectToMongoDB()

    documents = list(collection.find({"name": name}))
    for doc in documents:
        html = doc["HTML"]
        updatedHTML = doc["newHTML"]
        if html == updatedHTML:
            print("Same")
        else:
            print("The page has changed")
            sendEmail(rEmail, name)


def run(url, name, rEmail):
    logging.info("Started to look for updates on your page...")
    # while True:
    saveUpdatedHTML(url, name)
    time.sleep(5)
    print('5 seconds passed')
    verifyForUpdates(name, rEmail)
    updateInitialPage(name)


def sendEmail(email, name):
    logging.info("Started to prepare for sending the email...")
    t = time.localtime()
    d = datetime.date.today()

    senderEmail = constants.EMAIL
    password = constants.PASS
    receiverEmail = email
    subject = 'Awesome Crawler'
    current_time = time.strftime("%H:%M:%S", t)
    text = 'Pagina web ' + name + ' a fost modificata pe ' + d.strftime('%d-%m-%Y') + ' la ora ' + current_time
    message = 'Subject: {}\n\n{}'.format(subject, text)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(senderEmail, password)
    logging.info("Login success")
    s.sendmail(senderEmail, receiverEmail, message)
    logging.info("Email has been send to " + receiverEmail)


def deleteSavedPage(name, dbEmail):
    logging.info("Called function deletedSavedPage ...")
    collection = connectToMongoDB()
    myquery = {"name": name, "email": dbEmail}
    collection.delete_one(myquery)


def updateSavedPage(name, newName, newUrl, dbEmail):
    logging.info("Called function updateSavedPage ...")
    collection = connectToMongoDB()
    if newName != '':
        for doc in list(collection.find({"name": name, "email": dbEmail})):
            collection.update_one({"name": name, "email": dbEmail}, {"$set": {"name": newName}})
    elif newUrl != '':
        for doc in list(collection.find({"name": name, "email": dbEmail})):
            collection.update_one({"name": name, "email": dbEmail}, {"$set": {"HTML": newUrl}})
    else:
        for doc in list(collection.find({"name": name, "email": dbEmail})):
            collection.update_one({"name": name, "email": dbEmail}, {"$set": {"name": newName, "HTML": newUrl}})
    logging.info("Updated " + name)


def startTheApp():
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Welcome to the most awesome crawler!')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    mail = input('Please enter your email: ')
    option = principalMenu()
    if option == '0':
        sendAlert(mail)
    elif option == '1':
        createAlert(mail)
    elif option == '2':
        updateAlert(mail)
    elif option == '3':
        deleteAlert(mail)
    else:
        print('Invalid option!')
        startTheApp()


def principalMenu():
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Please select an action you want to perform:')
    print('0. Start sending alerts')
    print('1. Create a new alert')
    print('2. Update an existing alert')
    print('3. Delete an existing alert')
    option = input('Enter the number of your option here: ')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return option


def sendAlert(mail):
    print('--> Start sending alerts <--')
    collection = connectToMongoDB()
    while True:
        for doc in list(collection.find({"email": mail})):
            url = doc["url"]
            name = doc["name"]
            run(url, name, mail)


def createAlert(mail):
    print('--> Create a new alert <--')
    name = input('Please enter the name of the page you want to be notified about: ')
    url = input('Please enter the link of the page you want to be notified about: ')
    saveInitialPage(url, name, mail)
    startTheApp()


def updateAlert(mail):
    print('--> Update an existing alert <--')
    name = input('Please enter the name of the alert you want to change: ')
    newName = input('Please enter the the new name: ')
    newUrl = input('Please enter the the new url: ')
    updateSavedPage(name, newName, newUrl, mail)
    startTheApp()


def deleteAlert(mail):
    print('--> Delete an existing alert <--')
    name = input('Please enter the name of the alert you want to delete: ')
    deleteSavedPage(name, mail)
    startTheApp()


startTheApp()