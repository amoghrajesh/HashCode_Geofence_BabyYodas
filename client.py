########################################################
                    #Client
########################################################

################ packages ##############################
import re
import os
import ast
import requests
import json
import csv
import collections
from random import randint, uniform
from flask_api import status
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from flask import Flask, jsonify, request, abort, redirect, url_for, session, Response, _request_ctx_stack, render_template

#################### init ###############################
app = Flask(__name__)
app.config['SECRET_KEY'] = "client api"

headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
session_options = {'autocommit':False, 'autoflush':False}

ADMIN = "http://127.0.0.1:9999"
PORT = "5000"

################# function ######################

def get_location():
    return [12.9331912453213, 77.54340132194]
    # return [uniform(12.996800557961398, 12.91390750578042), uniform(77.45285487041474,77.59344553813935)]

################# apis ##########################

@app.route('/ping', methods=['POST'])
def getLocation():
    req = request.get_json()
    loc = get_location()
    payload = {'location': loc}
    return jsonify(payload)

@app.route('/')
def home():
	return render_template('login.html')

@app.route('/processLogin', methods=['POST'])
def processLogin():
    req = request.get_json()
    device_id = req['client_id']
    session['current_user'] = device_id
    session['user_available'] = True
    location = get_location()
    payload = {
                'device_id':device_id,
                'port': PORT,
                'location' : location
              }
    response = (requests.post(ADMIN+'/register', data = json.dumps(payload), headers = headers))
    # print(response, type(response))
    # ret = {}
    # ret['redirecturl'] = '/dashboard'
    # ret['msg'] = response['msg']
    return jsonify({"status": "OK"})

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if(session['user_available']):
	    return render_template('client_dashboard.html')
    return redirect(url_for('logout'))

@app.route('/updateDashboard', methods=['GET'])
def processDashboard():
    if(session['user_available']):
        location = get_location()
        payload = {
                'device_id': session['current_user'],
                'port': PORT,
                'location' : location
              }
        response = (requests.post(ADMIN+'/nearestGFS', data = json.dumps(payload), headers = headers)).json()
        return jsonify(response['results'])
    return redirect(url_for('logout'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if(session['user_available']):
        req = request.get_json()
        location = get_location()
        payload = {
                'device_id': session['current_user'],
                'port': PORT,
                'location' : location,
                'geof_id' : req['geof_id']
              }
        response = (requests.post(ADMIN+'/subscribe', data = json.dumps(payload), headers = headers)).json()
        return jsonify(response['msg'])
    return redirect(url_for('logout'))


@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    if(session['user_available']):
        req = request.get_json()
        location = get_location()
        payload = {
                'device_id': session['current_user'],
                'port': PORT,
                'location' : location,
                'geof_id' : req['geof_id'],
              }
        response = (requests.post(ADMIN+'/unsubscribe', data = json.dumps(payload), headers = headers)).json()
        return jsonify(response['msg'])
    return redirect(url_for('logout'))

@app.route('/partofGF', methods=['GET'])
def partofGF():
    if(session['user_available']):
        location = get_location()
        payload = {
                'device_id': session['current_user'],
                'port': PORT,
                'location' : location
              }
        response = (requests.post(ADMIN+'/partofGF', data = json.dumps(payload), headers = headers)).json()
        return jsonify(response['result'])
    return redirect(url_for('logout'))

@app.route('/logout')
def logout():
    session.clear()
    session['user_available'] = False
    session['current_user'] = ""
    return redirect(url_for('home'))


if __name__ == '__main__':	
	app.debug=True
	app.run(port=int(PORT))