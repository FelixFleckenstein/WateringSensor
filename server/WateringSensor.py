#!/usr/bin/env python

#import time
#import os
#import hashlib
#import json
#import thread
from datetime import datetime
#from datetime import timedelta

#from flask import Flask
#from flask import request
from flask import redirect
#from flask import render_template
from flask import make_response

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask import render_template_string

from flask import Flask, request, render_template
from werkzeug.serving import run_simple

# APP Settings
APP_SECRET_KEY = '7229ab3f61eaf19e48ff039cffa4768c07a3d6a34b8b99300048aded1d41fa1afc4113c1230ded7b5ffc08c9219c68098f715ed80099cb46b1621bc3cdc309ae'

__prefix__ = '/watering'

app = Flask("WateringSystem", static_url_path='/static')

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = APP_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///watering.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)

class wetness(db.Model):
	__tablename__ = 'wetness'
	ID = db.Column(db.Integer, primary_key=True)
	DATE = db.Column(db.DateTime, nullable=False)
	VALUE = db.Column(db.Float, nullable=False)
	Typ = db.Column(db.Text, nullable=False)

@app.route('/getPump', methods=['GET'])
def getPump():
	return "1"

@app.route('/', methods=['GET'])
def chart():
	data = reversed(db.session.query(wetness).filter_by(Typ='wet').order_by(desc(wetness.DATE)).limit(20).all())
	#reversed(conn.execute(query).fetchall())
	
	legend = ''
	values = []
	
	for allValues in data:		
		values.append(["new Date(" + str(allValues.DATE.year) + ", " + str(allValues.DATE.month) + ", " + str(allValues.DATE.day) + ", " + str(allValues.DATE.hour) + ", " + str(allValues.DATE.minute) + ")", allValues.VALUE])
		legend = allValues.VALUE
	
	
	#Temperatur
	data = reversed(db.session.query(wetness).filter_by(Typ='temp').order_by(desc(wetness.DATE)).limit(20).all())
	legendTemp = ''
	valuesTemp = []
	
	for allValues in data:		
		valuesTemp.append(["new Date(" + str(allValues.DATE.year) + ", " + str(allValues.DATE.month) + ", " + str(allValues.DATE.day) + ", " + str(allValues.DATE.hour) + ", " + str(allValues.DATE.minute) + ")", allValues.VALUE])
		legendTemp = allValues.VALUE
		
	#Luftfeuchtigkeit
	data = reversed(db.session.query(wetness).filter_by(Typ='air').order_by(desc(wetness.DATE)).limit(20).all())
	legendAir = ''
	valuesAir = []
	
	for allValues in data:		
		valuesAir.append(["new Date(" + str(allValues.DATE.year) + ", " + str(allValues.DATE.month) + ", " + str(allValues.DATE.day) + ", " + str(allValues.DATE.hour) + ", " + str(allValues.DATE.minute) + ")", allValues.VALUE])
		legendAir = allValues.VALUE

	aktFeuchte = db.session.query(wetness).filter_by(Typ='wet').order_by(desc(wetness.DATE)).limit(1).first()
	aktTemp = db.session.query(wetness).filter_by(Typ='temp').order_by(desc(wetness.DATE)).limit(1).first()
	aktLuft = db.session.query(wetness).filter_by(Typ='air').order_by(desc(wetness.DATE)).limit(1).first()

	#Temp via Zeit
	data = reversed(db.session.query(func.strftime("%Y-%m-%d", wetness.DATE), func.max(wetness.VALUE), func.min(wetness.VALUE)).group_by(func.strftime("%Y-%m-%d", wetness.DATE)).filter_by(Typ='temp').order_by(desc(wetness.DATE)).limit(6).all())
	valuesTempDays = []
	
	for allValues in data:
		valuesTempDays.append([allValues[0][8:]+"."+allValues[0][5:7], allValues[1], allValues[2]])
	
	return make_response(render_template('index.html', aktFeuchte=aktFeuchte.VALUE, aktTemp=aktTemp.VALUE, aktLuft=aktLuft.VALUE, values=values, legend=legend, valuesTemp=valuesTemp, legendTemp=legendTemp, valuesAir=valuesAir, legendAir=legendAir, valuesTempDays=valuesTempDays, prefix=__prefix__))	
	
@app.route('/add', methods=['GET', 'POST'])
def add():
	wet = request.args.get('moisture')
	temp = request.args.get('temperature')
	air = request.args.get('humidity')
	
	if(wet):
		type = "wet"
		dbValue = wet
		print("wet: ")
		print(wet)
		
	if(temp):
		type = "temp"
		dbValue = temp
		print("temp: ")
		print(temp)
		
	if(air):
		type = "air"
		dbValue = air
		print("air: ")
		print(air)
	
	#print(paramValue)
	#print(datetime.now())
	
	db.session.add(wetness(
		DATE = datetime.now(),
		VALUE = float(dbValue),
		Typ = type
	))

	db.session.commit()
	db.session.flush()

	return "ok"


run_simple('0.0.0.0', 8080, app, threaded=True)
