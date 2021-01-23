"""Initialize app."""
#!/usr/bin/env python
#'pip install pymsql, sqlalchemy'
from datetime import datetime
from sqlalchemy import (MetaData, Table, Column, Integer, Numeric, String, 
			DateTime, ForeignKey, create_engine, select)
#requires pyserial, install with 'pip install pyserial'
import serial

#print('Starting moisture sensor updater 2000')

metadata = MetaData()

#model our tables
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

#assign serial port
serial = serial.Serial('/dev/ttyACM0', 9600)

#create sqlalchemy engine
engine = create_engine('mysql+pymysql://databaseinfo here')

#init connection
connection = engine.connect()

#init metadata
metadata.create_all(engine)

#print('Connection to Database Established')
#print('Your sensor ID is 555')
#print('-----------------------------------')

#while 1:
#get serial port reading
line = serial.readline()
#print("The serial reading is %d", line)
date=datetime.now()

#insert statement
ins = sensorInfo.insert().values(
	sensorID="555",
	sensorTime=date,
	moistRead=line
	)
#print("The insert statement is: ")
#print(str(ins))
ins.compile().params
result = connection.execute(ins)
print('Table Insert Successful!')
#print('-----------------------------------')

#Select query
#s = select([plants])
#rp = connection.execute(s)
#results = rp.fetchall()

#print('ran query')

#print select query
#for record in rp:
	#print(record.plants.plantName)

#print('exiting')
