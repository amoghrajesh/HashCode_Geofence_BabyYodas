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
from random import randint
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

ADMIN = "localhost:9999"
PORT = "9998"

################# function ######################

def get_location():
    return [1,2]

################# apis ##########################

@app.route('/ping')
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
    device_id = request.form['device_id']
    session['current_user'] = device_id
    session['user_available'] = True
    location = get_location()
    payload = {
                'device_id':device_id,
                'port': PORT,
                'location' : location
              }
    response = (requests.post(ADMIN+'/register', data = json.dumps(payload), headers = headers)).json()
    if(response.status==200):
        ret = {}
        ret['redirecturl'] = '/dashboard'
    ret['msg'] = response['msg']
    return jsonify(ret)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if(session['user_available']):
	    return render_template('dashboard.html')
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
def unsubscribe():
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
	application.debug=True
	application.run(port=int(PORT))