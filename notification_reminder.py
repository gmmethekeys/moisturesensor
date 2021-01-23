"""Initialize app."""
# !/usr/bin/env python

#Created by Donald Marovich with full rights, not for reproduction or use without written consent from Donald Marovich

#scan for all possible sensorIDs, the cycle through each one
#if the reading is recent, cool, move on
#if the reading shows the plant needs water, cool, move on
#send an email


from datetime import datetime
from sqlalchemy import (MetaData, Table, Column, Integer, Numeric, String,
                        DateTime, ForeignKey, create_engine, select)
import smtplib
from email.mime.text import MIMEText

#from email import MIMEMultipart, MIMEText

# requires pyserial, install with 'pip install pyserial'
date = datetime.now()
metadata = MetaData()



# model our tables
plants = Table('plants', metadata,
               Column('id', Integer(), primary_key=True, nullable=False),
               Column('userID', Integer(), nullable=False),
               Column('plantName', String(100), nullable=False),
               Column('plantType', String(100), nullable=False),
               Column('PlantThirst', Integer(), nullable=False),
               Column('sensorID', Integer())
               )

sensorInfo = Table('sensorInfo', metadata,
                   Column('id', Integer(), primary_key=True, nullable=False),
                   Column('sensorID'),
                   Column('sensorTime', DateTime(), nullable=False),
                   Column('moistRead', Integer())
                   )

sensors = Table('sensors', metadata,
                Column('id', Integer, primary_key=True, nullable=False),
                Column('sensorID', Integer, nullable=False),
                Column('sensorName', String(100))
                )

users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(100), nullable=False, unique=False),
              Column('email', String(40), unique=True, nullable=False),
              Column('password', String(200), primary_key=False, unique=False, nullable=False),
              Column('website', String(60), index=False, unique=False, nullable=True),
              Column('created_on', DateTime(), index=False, unique=False, nullable=True),
              Column('last_login', DateTime(), index=False, unique=False, nullable=True)
              )


# create sqlalchemy engine
engine = create_engine(
    'mysql+pymysql://morthos:afcbdfag38@projectgardenapp.czycyhu4wgvm.us-west-2.rds.amazonaws.com:3306/garden_app')

# init connection
connection = engine.connect()

# init metadata
metadata.create_all(engine)

print('Connected to Database')
print('------------------------------------------')


#create variable to store email
email1 = ""
moistRead1 = ""
lastReading = ""
plantName1 = ""
#currently passing a testID, need this to test all known IDs
currentsensorID = '555'
sensorIDlist = ""
currentplantstatus = "A status should be here."
plantThirst = ""
results = ""


#query definitions
def getEmail():
    # Select email
    query = connection.execute('SELECT u.email FROM users u INNER JOIN plants p ON u.id = p.userID INNER JOIN sensorInfo s ON p.sensorID = s.sensorID LIMIT 1;')
    return query


def moistureReading(currentsensorID):
    currentsensorID = currentsensorID
    query2 = connection.execute('SELECT s.moistRead, s.sensorTime, p.plantName FROM sensorInfo s INNER JOIN plants p ON s.sensorID = p.sensorID WHERE p.sensorID = \'%s\' ORDER BY s.sensorTime DESC LIMIT 1;' % currentsensorID)
    return query2


def getSensorID():
    query3 = connection.execute('SELECT sensorID FROM garden_app.sensors;')
    return query3

def getThirstLevel(currentsensorID):
    #query4 = connection.execute('SELECT plantThirst from plants WHERE sensorID = \'%s\';' % currentsensorID)
    #query4 = connection.execute('SELECT plantThirst from plants WHERE sensorID = 555;')
    #query4 = engine.query(plants).filter(sensorID == currentsensorID)
    query4 = select([plants])
    rp = connection.execute(query4)
    results = rp.fetchall()
    return results


def sendEmail(plantName1, sensorID, currentplantstatus):

    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    textfile = '/home/pi/Desktop/Code/textfile.txt'
    fp = open(textfile, 'rb')

    # Create a text/plain message
    msg = MIMEText(fp.read())
    fp.close()

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = 'It is time to water %s' % plantName1
    msg['From'] = "water.reminder.garden@gmail.com"
    msg['To'] = email1

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('water.reminder.garden@gmail.com', 'WaterSecretGarden')
    s.sendmail("water.reminder.garden@gmail.com", email1, msg.as_string())
    s.quit()


#run querys
query = getEmail()
query2 = moistureReading(currentsensorID)
#query3 = getSensorID()
query4 = getThirstLevel(currentsensorID)

#get the email and store it into variable
for row in query:
    email1 = row[0]
    #print(row[0])

#assign moisture reading, and plant name to variables
for row in query2:
    moistRead1 = row[0]
    lastReading = row[1]
    plantName1 = row[2]

#print(results)

for row in query4:
    plantThirst = row[0]

print("Plant Thirst Value is: %s" % plantThirst)

#Default setting if no thirst level set
if plantThirst == 0:
    # plantThirst level 5 (DEFAULT)
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    # reading between 10-300
    if (moistRead1 > 11 and moistRead1 < 300):
        currentplantstatus = "The plant has too much water."

    # reading betewen 301-350
    if (moistRead1 > 301 and moistRead1 < 350):
        currentplantstatus = "The plant is well watered."

    # reading between 351-400
    if (moistRead1 > 351 and moistRead1 < 400):
        currentplantstatus = "The plant is well watered."

    # reading betewen 401-430
    if (moistRead1 > 401 and moistRead1 < 430):
        currentplantstatus = "The plant is starting to get thirsty."

    # reading above 431
    if (moistRead1 > 431):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 1:
    # plantThirst level 1
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 300):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 301 and moistRead1 < 350):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 351 and moistRead1 < 430):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 430 and moistRead1 < 449):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 450):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')



if plantThirst == 2:
    # plantThirst level 5
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 300):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 301 and moistRead1 < 350):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 351 and moistRead1 < 400):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 401 and moistRead1 < 429):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 430):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 3:
    # plantThirst level 3
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 300):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 301 and moistRead1 < 350):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 351 and moistRead1 < 400):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 401 and moistRead1 < 409):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 410):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 4:
    # plantThirst level 4
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 300):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 301 and moistRead1 < 350):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 351 and moistRead1 < 369):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 370 and moistRead1 < 389):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 390):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 5:
    # plantThirst level 5
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 300):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 301 and moistRead1 < 319):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 320 and moistRead1 < 349):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 350 and moistRead1 < 369):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 370):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 6:
    #plantThirst level 6
    #readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 249):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 250 and moistRead1 < 279):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 280 and moistRead1 < 299):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 300 and moistRead1 < 349):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 350):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 7:
    # plantThirst level 7
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 200):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 201 and moistRead1 < 220):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 221 and moistRead1 < 250):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 251 and moistRead1 < 339):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 340):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 8:
    # plantThirst level 8
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 200):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 201 and moistRead1 < 220):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 221 and moistRead1 < 250):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 251 and moistRead1 < 329):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 330):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 9:
    # plantThirst level 9
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 200):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 201 and moistRead1 < 220):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 221 and moistRead1 < 250):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 251 and moistRead1 < 319):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 320):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')

if plantThirst == 10:
    # plantThirst level 10
    # readings below 10 (aka in nothing but water)
    if (moistRead1 < 10):
        currentplantstatus = "The plant fell into a lake or pond..."

    if (moistRead1 > 11 and moistRead1 < 200):
        currentplantstatus = "The plant has too much water."

    if (moistRead1 > 201 and moistRead1 < 220):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 221 and moistRead1 < 250):
        currentplantstatus = "The plant is well watered."

    if (moistRead1 > 251 and moistRead1 < 309):
        currentplantstatus = "The plant is starting to get thirsty."

    if (moistRead1 > 310):
        currentplantstatus = "The plant needs to be watered."
        sendEmail(plantName1, currentsensorID, currentplantstatus)
        print('Email was sent.')


#print(type(query3))
#print(type(sensorIDlist))

#The ResultProxy object is made up of RowProxy objects
#The RowProxy object has an .items() method that returns key, value tuples of all the items in the row

#get sensorIDs into array
# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
'''
d, a = {}, []
for row in query3:
    for column,  value in rowproxy.items():
        #build dictionary
        d = {**d, **{column: value}}
    a.append(d)
   

def read(query):
    results = []

    for row_number, row in enumerate(query):
        results.append({})
        for column_number, value in enumerate(row):
            results[row_number][row.keys()[column_number]] = value
        return results

read(query3)

print(results)
#print(sensorIDlist)
#print(sensorIDlist.len())
'''

print('Query is done')
print('------------------------------------------')
print('The email is: %s' % email1)
print('------------------------------------------')
print('The moisture reading is: %s' % moistRead1)
print('------------------------------------------')
print('The time of reading is: %s' % lastReading)
print('------------------------------------------')
print('The plant name is: %s' % plantName1)
print('------------------------------------------')
print('The plant status is: %s' % currentplantstatus)
print('------------------------------------------')

#sendEmail()



print('Exiting Program')
