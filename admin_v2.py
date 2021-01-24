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
session1 = dict()
session1['user_available'] = True

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
    port = db.Column(db.String(), index=True)
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
    if(session1['user_available']):
	    return render_template('admin_dashboard.html')
    return redirect(url_for('logout'))

#Do rest/ajax on this
@app.route('/updateDashboard', methods=['GET'])
def processDashboard():
    if(session1['user_available']):
        resu = db.session.query(Geofence).all()
        ret = {}
        for row in resu:
            devices = row.joined_devices.split('#')
            print("dddddddddddd", devices)
            if devices == ['']:
                return jsonify({" ": ""}) 
            ret[row.geof_id] = []
            for device_id in devices:
                resp = db.session.query(Device).filter_by(device_id=device_id).first() 
                print("resp ----- ", resp)
                if resp is None:
                    return jsonify({"skip": "ok"})   
                port = resp.port
                #ping client for location
                #(lat, lon) = pingClient(device_id)
                payload = {'device_id': device_id}
                print("port ------------------------", port)
                response = (requests.post('http://127.0.0.1:'+ port + '/ping', data = json.dumps(payload), headers = headers)).json()
                print("response ---------------", response)
                lat, lon = response['location']
                float_latitudes = [float(x) for x in row.latitudes.split('#')]
                float_longitudes = [float(x) for x in row.longitudes.split('#')] 
                ###########################################check lat, long #########################
                if row.fence_type == "circle":
                    (status, dist, coords) = GetStatus(row.fence_type, ast.literal_eval(row.centroid), float_latitudes, float_longitudes, float(row.boundary_buffer), (lat, lon), float(row.radius))
                else:
                    (status, dist, coords) = GetStatus(row.fence_type, ast.literal_eval(row.centroid), float_latitudes, float_longitudes, float(row.boundary_buffer), (lat, lon), "")
                if status==1:
                    dist = -dist
                ret[row.geof_id].append([device_id, status, dist, list(coords)])
        return jsonify(ret)
    return redirect(url_for('logout'))

@app.route('/createGfence', methods=['GET'])
def createGfence():
    if(session1['user_available']):
	    return render_template('gmap.html')
    return redirect(url_for('logout'))

@app.route('/processCreateGfence', methods=['POST'])
def processCreateGfence():
    if(session1['user_available']):
        ret = {}
        req = request.get_json()
        #admin_id = (request.form['admin_id']).strip()
        geof_id = req['geof_id']
        shape = req['type']
        radius = req['radius']
        ##############################check what type
        if shape != "circle":
            latitude = []
            longitude = []
            locations = ast.literal_eval(req['locations'])
            locations = list(locations)
            # print(locations, type(locations))

            for loc in locations:
                latitude.append(loc[0])
                longitude.append(loc[1])
        else:
            latitude = [req['latitude']]
            longitude = [req['longitude']]
        
        latitudes = latitude
        longitudes = longitude
        quer_res = db.session.query(Geofence).filter_by(geof_id = geof_id)
        if(quer_res.scalar() is None):
            #compute centroid and buffer distance
            centroid = Centroid(shape,latitudes,longitudes,radius)
            buffer_dist = CalculateBufferDistance(shape,latitudes,longitudes,radius)
            #################################check type of lat and long before join
            str_latitudes = [str(x) for x in latitudes]
            str_longitudes = [str(x) for x in longitudes]
            reg = Geofence(randint(1, 100000), shape, str(radius), str(centroid), "#".join(str_latitudes), "#".join(str_longitudes), "", str(buffer_dist))
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
    return redirect('http://127.0.0.1:9999/')


@app.route('/register', methods=['POST'])
def registerDevice():
    if(session1['user_available']):
        ret = {}
        req = request.get_json()
        print("###########################################################################")
        print(req)
        device_id = (req['device_id'])
        port = (req['port'])
        loc = req['location']
        quer_res = db.session.query(Device).filter_by(device_id = device_id)
        if(quer_res.scalar() is None):
            reg = Device(device_id, port, "", "", "", "")
            db.session.add(reg)
            db.session.commit()
            print({"msg":"success!"})
            return jsonify({"msg":"success!"})
        else:
            print({"msg":"exists already!"})
            return jsonify({"msg":"exists already!"})
    return jsonify({"msg":"fail!"})

@app.route('/nearestGFS', methods=['POST'])
def nearestGFS():
    if(session1['user_available']):
        geofences = {}
        req = request.get_json()
        x=0.0005
        resu = db.session.query(Geofence).all()
        for row in resu:
            float_latitudes = [float(x) for x in row.latitudes.split('#')]
            float_longitudes = [float(x) for x in row.longitudes.split('#')] 
            
            if row.fence_type != "circle":
                geofences[row.geof_id] = {'centroid': ast.literal_eval(row.centroid), 'rad':"", 'type':row.fence_type , 'latitudes':float_latitudes ,'longitudes': float_longitudes }
            else:
                geofences[row.geof_id] = {'centroid': ast.literal_eval(row.centroid), 'rad':float(row.radius), 'type':row.fence_type, 'latitudes':float_latitudes ,'longitudes': float_longitudes }
        
        ngfs = GetGeoFence(geofences, x, req['location'])
        return jsonify({'results': ngfs})
    return jsonify({'msg':'fail!'})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if(session1['user_available']):
        ret = {}
        req = request.get_json()
        quer_res = db.session.query(Geofence).filter_by(geof_id = req['geof_id']).first()
        joined_devices = quer_res.joined_devices
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
            fences_joined = quer_res.joined_fences
            if(len(fences_joined)==0):
                new_fences_joined =  req['geof_id']
            else:
                new_fences_joined = fences_joined+'#'+req['geof_id']
            db.session.query(Device).filter_by(device_id=req['device_id']).update(dict(joined_fences=new_fences_joined))
            db.session.commit()
            ret['msg'] = "subscribed!"
        return jsonify(ret)
    return jsonify({"msg":"failed!"})        
            
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    if(session1['user_available']):
        ret = {}
        req = request.get_json()
        quer_res = db.session.query(Geofence).filter_by(geof_id = req['geof_id']).first()
        joined_devices = ((quer_res.joined_devices).split('#')).remove(req['device_id'])
        if len(joined_devices) == 0:
            joined_devices = ''
        else:
            joined_devices = '#'.join(joined_devices)
        db.session.query(Geofence).filter_by(geof_id=req['geof_id']).update(dict(joined_devices=joined_devices))
        db.session.commit()
        quer_res = db.session.query(Device).filter_by(device_id = req['device_id']).first()
        joined_fences = ((quer_res.joined_fences).split('#')).remove(req['geof_id'])

        if len(joined_fences) == 0:
            joined_fences = ''
        else:
            joined_fences = '#'.join(joined_fences)

        db.session.query(Device).filter_by(device_id=req['device_id']).update(dict(joined_fences=joined_fences))
        db.session.commit()
        return jsonify({"msg": "success!"})
    return jsonify({'msg': 'fail!'})

@app.route('/partofGF', methods=['POST'])
def partofGF():
    if(session1['user_available']):
        ret = {}
        req = request.get_json()
        quer_res = db.session.query(Device).filter_by(device_id=req['device_id']).first()            
        fences_joined = (quer_res.fences_joined).split('#')
        ret['results'] = fences_joined
        return ret
    return jsonify({'msg':'fail!'})


from MergeGeofence import *
@app.route('/convexhull', methods=['GET']) #GET
def convexhull():
    if(session1['user_available']):
        resu = db.session.query(Geofence).all()
        ret = {}
        for row in resu:
            geof_id = row.geof_id
            lat = row.latitudes
            lon = row.longitudes
            float_lat = [float(x) for x in lat.split('#')]
            float_lon = [float(x) for x in lon.split('#')]
            ret[geof_id] = {"Latitudes":float_lat, "Longitudes": float_lon}
        merged_geof = merge(ret)
        return merged_geof

if __name__ == '__main__':
    app.debug=True
    app.run(port=9999)