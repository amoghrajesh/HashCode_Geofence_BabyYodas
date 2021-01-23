########################################################
                """geofence admin"""
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
app.config['SECRET_KEY'] = "geofence api"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///geofence.db'

headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
session_options = {'autocommit':False, 'autoflush':False}
db = SQLAlchemy(app)

###################### db ###############################
class Admin(db.Model):
    __tablename__ = "admin"
    a_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.String(), unique=True, index=True)
    owns_fences = db.Column(db.String(), nullable=False)

    def __init__(self, admin_id, owns_fences):
        self.device_id = device_id
        self.owns_fences = owns_fences

class Geofence(db.Model):
    __tablename__ = "geofence"
    fence_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.String(), nullable=False)
    geof_id = db.Column(db.String(), unique=True, nullable=False)
    fence_type = db.Column(db.String(), nullable=False)
    radius = db.Column(db.String(), nullable=False)
    centroid = db.Column(db.String(), nullable=False)
    latitudes = db.Column(db.String(), nullable=False)
    longitudes = db.Column(db.String(), nullable=False)
    joined_devices = db.Column(db.String(), nullable=False)
    boundary_buffer = db.Column(db.String(), nullable=False)
    

    def __init__(self, geof_id, admin_id, fence_type, radius, centroid, latitudes, longitudes, joined_devices, boundary_buffer):
        self.admin_id = admin_id
        self.geof_id = geof_id
        self.fence_type = fence_type
        self.radius = radius
        self.centroid = centroid
        self.latitudes = latitudes
        self.longitudes = longitudes
        self.joined_devices = joined_devices
        self.boundary_buffer = boundary_buffer

class Device(db.Model):
    __tablename__ = "device"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(), unique=True, index=True)
    joined_fences = db.Column(db.String(), nullable=False)
    #optional, dynamic:
    latitude = db.Column(db.String(), nullable=False) 
    longitude = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False) #inside/outside for each fence subscribed to

    def __init__(self, device_id, joined_fences, latitude, longitude, status):
        self.device_id = device_id
        self.joined_fences = joined_fences
        self.latitude = latitude
        self.longitude = longitude
        self.status = status

db.create_all()

################ functions ####################

################# apis ##########################

@app.route('/')
def home():
	return render_template('login.html')

@app.route('/processLogin', methods=['POST'])
def processLogin():
    admin_id = request.form['admin_id']
    session['current_user'] = admin_id
    session['user_available'] = True
    quer_res = db.session.query(Admin).filter_by(admin_id = admin_id)
    ret = {}
    ret['redirecturl'] = '/dashboard'
    if(quer_res.scalar() is None):
        reg = Admin(admin_id,"")
        db.session.add(reg)
        db.session.commit()
    ret['msg'] = "Successfully created!"
    return jsonify(ret)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if(session['user_available']):
	    return render_template('dashboard.html')
    return redirect(url_for('logout'))

#Do rest/ajax on this
@app.route('/updateDashboard', methods=['GET'])
def processDashboard():
    if(session['user_available']):
        resu = db.session.query(Geofence).filter_by(admin_id=session['current_user'])
        ret = {}
        for row in resu:
            devices = row['joined_devices'].split('#')
            for device_id in devices:
                #resp = db.session.query(Device).filter_by(device_id=device_id)    
                #ping client for location
                (lat, lon) = pingClient(device_id)
                ###########################################check lat, long #########################
                (status, dist, coords) = GetStatus(row['type'], row['centroid'], row['latitudes'], row['longitudes'], row['boundary_buffer'], (lat, lon), row['radius'])
                if status==1:
                    dist = -dist
                ret[resu['geof_id']].append(device_id, status, dist, list(coords))
        return jsonify(ret)
    return redirect(url_for('logout'))

@app.route('/createGfence', methods=['GET'])
def createGfence():
    if(session['user_available']):
	    return render_template('geof.html')
    return redirect(url_for('logout'))

@app.route('/processCreateGfence', methods=['POST'])
def processCreateGfence():
    if(session['user_available']):
        ret = {}
        admin_id = (request.form['admin_id']).strip()
        geof_id = (request.form['geof_id']).strip()
        shape = (request.form['type']).strip()
        radius = (request.form['radius']).strip()
        ##############################check what type
        latitudes = request.form['latitudes']
        longitudes = request.form['longitudes']
        quer_res = db.session.query(Geofence).filter_by(geof_id = geof_id)
        if(quer_res.scalar() is None):
            #compute centroid and buffer distance
            centroid = Centroid(shape,latitudes,longitudes,radius)
            buffer_dist = CalculateBufferDistance(shape,latitudes,longitudes,radius)
            #################################check type of lat and long before join
            reg = Geofence(admin_id, geof_id, shape, radius, centroid, "#".join(latitudes), "#".join(longitudes), "", buffer_dist)
            db.session.add(reg)
            db.session.commit()
        else:
            return jsonify({'error' : 'Fence already exists !'}) 

    return redirect(url_for('logout'))

@app.route('/logout')
def logout():
    session.clear()
    session['user_available'] = False
    session['current_user'] = ""
    return redirect(url_for('home'))

"""
@app.route('/register', methods=['POST'])
def processCreateGfence():
    if(session['user_available']):
        ret = {}
        admin_id = (request.form['admin_id']).strip()
        geof_id = (request.form['geof_id']).strip()
        shape = (request.form['type']).strip()
"""

if __name__ == '__main__':	
	application.debug=True
	application.run(port=9999)