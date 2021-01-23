########################################################
                #geofence admin
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

from functions import *

#################### init ###############################
app = Flask(__name__)
app.config['SECRET_KEY'] = "geofence api"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///geofence.db'

headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
session_options = {'autocommit':False, 'autoflush':False}
db = SQLAlchemy(app)

###################### db ###############################
"""
class Admin(db.Model):
    __tablename__ = "admin"
    a_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.String(), unique=True, index=True)
    owns_fences = db.Column(db.String(), nullable=False)

    def __init__(self, admin_id, owns_fences):
        self.device_id = device_id
        self.owns_fences = owns_fences
"""
class Geofence(db.Model):
    __tablename__ = "geofence"
    fence_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #admin_id = db.Column(db.String(), nullable=False)
    geof_id = db.Column(db.String(), unique=True, nullable=False)
    fence_type = db.Column(db.String(), nullable=False)
    radius = db.Column(db.String(), nullable=False)
    centroid = db.Column(db.String(), nullable=False)
    latitudes = db.Column(db.String(), nullable=False)
    longitudes = db.Column(db.String(), nullable=False)
    joined_devices = db.Column(db.String())
    boundary_buffer = db.Column(db.String(), nullable=False)
    

    def __init__(self, geof_id, fence_type, radius, centroid, latitudes, longitudes, joined_devices, boundary_buffer):
        #self.admin_id = admin_id
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
    d_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(), unique=True, index=True)
    port = db.Column(db.String(), unique=True, index=True)
    joined_fences = db.Column(db.String())
    #optional, dynamic:
    latitude = db.Column(db.String()) 
    longitude = db.Column(db.String())
    status = db.Column(db.String()) #inside/outside for each fence subscribed to

    def __init__(self, device_id, port, joined_fences, latitude, longitude, status):
        self.device_id = device_id
        self.port = port
        self.joined_fences = joined_fences
        self.latitude = latitude
        self.longitude = longitude
        self.status = status

db.create_all()

################ functions ####################

################# apis ##########################
"""
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
"""
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if(session['user_available']):
	    return render_template('dashboard.html')
    return redirect(url_for('logout'))

#Do rest/ajax on this
@app.route('/updateDashboard', methods=['GET'])
def processDashboard():
    if(session['user_available']):
        resu = db.session.query(Geofence).all()
        ret = {}
        for row in resu:
            devices = row['joined_devices'].split('#')
            ret[resu['geof_id']] = []
            for device_id in devices:
                resp = db.session.query(Device).filter_by(device_id=device_id)    
                port = resp['port']
                #ping client for location
                #(lat, lon) = pingClient(device_id)
                payload = {'device_id': device_id}
                response = (requests.post('localhost:'+port+'/ping', data = json.dumps(payload), headers = headers)).json()
                lat, lon = response['location']
                ###########################################check lat, long #########################
                (status, dist, coords) = GetStatus(row['type'], float(row['centroid']), float(row['latitudes']), float(row['longitudes']), float(row['boundary_buffer']), (lat, lon), float(row['radius']))
                if status==1:
                    dist = -dist
                ret[resu['geof_id']].append([device_id, status, dist, list(coords)])
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
        req = request.get_json()
        #admin_id = (request.form['admin_id']).strip()
        geof_id = (req['geof_id']).strip()
        shape = (req['type']).strip()
        radius = (req['radius'])
        ##############################check what type
        latitudes = req['latitudes']
        longitudes = req['longitudes']
        quer_res = db.session.query(Geofence).filter_by(geof_id = geof_id)
        if(quer_res.scalar() is None):
            #compute centroid and buffer distance
            centroid = Centroid(shape,latitudes,longitudes,radius)
            buffer_dist = CalculateBufferDistance(shape,latitudes,longitudes,radius)
            #################################check type of lat and long before join
            str_latitudes = [str(x) for x in latitudes]
            str_longitudes = [str(x) for x in longitudes]
            reg = Geofence(geof_id, shape, str(radius), str(centroid), "#".join(latitudes), "#".join(longitudes), "", str(buffer_dist))
            db.session.add(reg)
            db.session.commit()
        else:
            return jsonify({'error' : 'Fence already exists !'}) 

    return redirect(url_for('logout'))

@app.route('/logout')
def logout():
    #session.clear()
    #session['user_available'] = False
    #session['current_user'] = ""
    return redirect(url_for('home'))


@app.route('/register', methods=['POST'])
def registerDevice():
    if(session['user_available']):
        ret = {}
        req = request.get_json()
        device_id = (req['device_id'])
        port = (req['port'])
        loc = req['location']
        quer_res = db.session.query(Device).filter_by(device_id = device_id)
        if(quer_res.scalar() is None):
            reg = Device(device_id, port, "")
            db.session.add(reg)
            db.session.commit()
            return {"msg":"success!"}
        else:
            return {"msg":"exists already!"}
    return {"msg":"fail!"}, 400

@app.route('/nearestGFS', methods=['POST'])
def nearestGFS():
    if(session['user_available']):
        geofences = {}
        req = request.get_json()
        x=0.0005
        resu = db.session.query(Geofence).all()
        for row in resu:
            float_latitudes = [float(x) for x in row['latitudes']]
            float_longitudes = [float(x) for x in row['longitudes']] 
            geofences[row['geof_id']] = {'rad':float(radius), 'type':row['fence_type'] ,'centroid':float(row['centroid']), 'lat':float_latitudes ,'long': float_longitudes }
        ngfs = GetGeoFence(geofences, x, req['location'])
        return {'results': ngfs}
    return {'msg':'fail!'}

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if(session['user_available']):
        ret = {}
        req = request.get_json()
        quer_res = db.session.query(Geofence).filter_by(geof_id = req['geof_id']).first()
        joined_devices = quer_res['joined_devices']
        if(req['device_id'] in joined_devices):
            ret['msg'] = 'already subscribed!'
        else:
            if(len(joined_devices)==0):
                new_joined_devices = req['device_id']
            else:
                new_joined_devices = joined_devices+'#'+req['device_id']
            db.session.query(Geofence).filter_by(geof_id=req['geof_id']).update(dict(joined_devices=new_joined_devices))
            db.session.commit()

            quer_res = db.session.query(Device).filter_by(device_id=req['device_id']).first()            
            fences_joined = quer_res['fences_joined']
            if(len(fences_joined)==0):
                new_fences_joined =  req['geof_id']
            else:
                new_fences_joined = fences_joined+'#'+req['geof_id']
            db.session.query(Device).filter_by(device_id=req['device_id']).update(dict(fences_joined=new_fences_joined))
            db.session.commit()
            ret['msg'] = "subscribed!"
        return ret
    return {"msg":"failed!"}        
            
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    if(session['user_available']):
        ret = {}
        req = request.get_json()
        quer_res = db.session.query(Geofence).filter_by(geof_id = req['geof_id']).first()
        joined_devices = ((quer_res['joined_fences']).split('#')).remove(req['device_id'])
        db.session.query(Geofence).filter_by(geof_id=req['geof_id']).update(dict(joined_devices=joined_devices))
        db.session.commit()
        quer_res = db.session.query(Device).filter_by(device_id = req['device_id']).first()
        joined_fences = ((quer_res['fences_joined']).split('#')).remove(req['geof_id'])
        db.session.query(Device).filter_by(device_id=req['device_id']).update(dict(fences_joined=fences_joined))
        db.session.commit()
        return {"msg": "success!"}
    return {'msg': 'fail!'}

@app.route('/partofGF', methods=['POST'])
def partofGF():
    if(session['user_available']):
        ret = {}
        req = request.get_json()
        quer_res = db.session.query(Device).filter_by(device_id=req['device_id']).first()            
        fences_joined = (quer_res['fences_joined']).split('#')
        ret['results'] = fences_joined
        return ret
    return {'msg':'fail!'}

if __name__ == '__main__':
    session['user_available'] = True	
	application.debug=True
	application.run(port=9999)