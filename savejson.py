from flask import Flask, render_template,abort,request
import requests
import json
import ast
app = Flask(__name__)


@app.route("/",methods=["GET"])
def index_page():
    return render_template("gmap.html")

@app.route("/test", methods=["GET"])
def test():
    return "test"

@app.route("/save", methods=["POST"])
def save():
    req = request.get_json()
    # req = json.loads(req)
    print(req)
    tosave = dict()
    tosave['admin_id'] = req['admin_id']
    tosave['type'] = req['type']
    tosave['radius'] = req['radius']

    latitude = []
    longitude = []
    locations = x = ast.literal_eval(req['locations'])
    # print(locations, type(locations))

    for loc in locations:
        latitude.append(loc[0])
        longitude.append(loc[1])
    
    tosave['latitudes'] = latitude
    tosave['longitudes'] = longitude

    with open("common_resources/sample.json", "w") as outfile: 
        outfile.write(json.dumps(tosave))

    return "Saved Succesfully"

if __name__ == "__main__" :
    app.run(debug=True)