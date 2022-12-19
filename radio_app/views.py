from django.shortcuts import render
from django.http import HttpResponse
import sqlite3
import json
import html

# Create your views here.
app_name = "radio_app"



def index(request):
    return HttpResponse("Success")

def list_stations(request):
    db = sqlite3.connect("station_data.sqlite3")
    stations = db.execute("SELECT station_id, station_name FROM stations;")
    stations= str(dict(stations))
    stations = json.dumps(stations)
    return HttpResponse(stations)

def get_station(request, id):
    db = sqlite3.connect("station_data.sqlite3")
    station = db.execute("SELECT station_id, station_name, stream_url FROM stations WHERE station_id=" + str(id) + ";")

    # return a json object of a station id, station name, and streamurl
    station= list(station)
    if station:
        station = str({"id":station[0][0], "name": station[0][1], "stream_url": station[0][2]})
        station = json.dumps(station)
    else:
        station = json.dumps(str({"error": "Station not found."}))
    return HttpResponse(station)

def get_user(request, usern):
    db = sqlite3.connect("station_data.sqlite3")
    user = db.execute(f"SELECT message FROM users WHERE username = '{str(usern)}';")
    user = list(user)

    # return a json object containing user's messages and message count
    if user:
        user = list([str(u[0]) for u in user])
        user = {"name": usern, "messages": user, "count":str(len(user))}
        user = json.dumps(str(user))
    else:
        user = json.dumps(str({"error": "User not found."}))
    
    return HttpResponse(user)
def add_station(request):
    id=name=stream_url=""
    try:
        id=int(request.GET["id"])
        name=html.escape(request.GET["name"])
        stream_url=html.escape(request.GET["stream_url"])
    except:
        response = json.dumps(str({"error": "Invalid Input"}))
    
    if (not id) or (not name) or (not stream_url):
        return HttpResponse(response)

    db = sqlite3.connect("station_data.sqlite3")

    check_id = list(db.execute(f"SELECT * FROM stations WHERE station_id = '{id}';"))

    if not check_id:
        db.execute(f"INSERT INTO stations(station_id, station_name, stream_url) VALUES({id}, '{name}', '{stream_url}');")
        db.commit()
        response = json.dumps(str({"Success": "Added station."}))
    else:
        response = json.dumps(str({"error": "Station ID exists."}))
    # print(id, name, stream_url)
    
    return HttpResponse(response)

