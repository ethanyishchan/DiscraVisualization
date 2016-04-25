# author: oskar.blom@gmail.com
#
# Make sure your gevent version is >= 1.0
import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

from flask import Flask, Response

import time

import random, glob, os, uuid, urllib2, time, httplib, urllib, requests, json

from flask_googlemaps import GoogleMaps, Map
from kafka import KafkaConsumer
from pykafka import KafkaClient
from flask import Flask, request,render_template, jsonify, Response, session
from flask.ext.cache import Cache
import numpy as np

#constants
#lake lagunita GPS coordinates
base_lat = 37.422570
base_long = -122.176514

#change this to whatever the gufi is right now
gufi_1 = '3d64802e-97d5-444c-ac21-d1a5decb69dd'
gufi_2 = 'fc7df749-a26f-426c-ac6c-25f1c98ca399'

# SSE "protocol" is described here: http://mzl.la/UPFyxY
class ServerSentEvent(object):

    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data : "data",
            self.event : "event",
            self.id : "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k) 
                 for k, v in self.desc_map.iteritems() if k]
        
        return "%s\n\n" % "\n".join(lines)

app = Flask(__name__)
subscriptions = []
advisory_subscriptions_1 = []
advisory_subscriptions_2 = []
advisory_subscriptions_3 = []

@app.route("/debug")
def debug():
    return "Currently %d subscriptions" % len(subscriptions)


# Client code consumes like this.
@app.route("/")
def index():
    print subscriptions

    mymap = Map(
    identifier="view-side",
    lat=37.4419,
    lng=-122.1419,
    markers=[(37.4419, -122.1419)])

    sndmap = Map(
    identifier="sndmap",
    lat=37.4419,
    lng=-122.1419,
    markers={'http://maps.google.com/mapfiles/ms/icons/green-dot.png':[(37.4419, -122.1419)],
             'http://maps.google.com/mapfiles/ms/icons/blue-dot.png':[(37.4300, -122.1400)]})

    return render_template('main_map.html', mymap = mymap, sndmap = sndmap)


#receive incoming advisories from kafka server
@app.route("/consume_advisory_live", methods=['POST', 'GET'])
def consume_advisory_live():
    msg = request.data

    advisory_array = json.loads(msg)
    # print advisory_array

    def notify(m, adv_subs):
        for sub in adv_subs[:]:
            sub.put(m)

    for gufi_adv in advisory_array:
        if gufi_adv["gufi"] == gufi_1:
            gufi_adv["gufi"] = "drone1"
        if gufi_adv["gufi"] == gufi_2:
            gufi_adv["gufi"] = "drone2"


        curr_lat = float(gufi_adv['waypoints'][0]["lat"])
        curr_lon = float(gufi_adv['waypoints'][0]["lon"])
        new_lat, new_lon = lat_lon_convert(curr_lat,curr_lon)
        gufi_adv['waypoints'][0]["lat"] = str(new_lat)
        gufi_adv['waypoints'][0]["lon"] = str(new_lon)
        gufi_msg = json.dumps(gufi_adv)
        if gufi_adv["gufi"] == "drone1":
            gevent.spawn(notify(  gufi_msg,    advisory_subscriptions_1))
        elif gufi_adv["gufi"] == "drone2":
            gevent.spawn(notify(  gufi_msg,    advisory_subscriptions_2))
        else:
            gevent.spawn(notify(  gufi_msg,    advisory_subscriptions_3))

    # gevent.spawn(notify(msg))
    return "OK"

#receive incoming advisories from kafka server
@app.route("/consume_advisory", methods=['POST', 'GET'])
def consume_advisory():
    msg = request.data

    advisory_array = json.loads(msg)
    # print advisory_array

    def notify(m, adv_subs):
        for sub in adv_subs[:]:
            sub.put(m)

    for gufi_adv in advisory_array:
        curr_lat = float(gufi_adv['waypoints'][0]["lat"])
        curr_lon = float(gufi_adv['waypoints'][0]["lon"])
        new_lat, new_lon = lat_lon_convert(curr_lat,curr_lon)
        gufi_adv['waypoints'][0]["lat"] = str(new_lat)
        gufi_adv['waypoints'][0]["lon"] = str(new_lon)
        gufi_msg = json.dumps(gufi_adv)
        if gufi_adv["gufi"] == "drone1":
            gevent.spawn(notify(  gufi_msg,    advisory_subscriptions_1))
        elif gufi_adv["gufi"] == "drone2":
            gevent.spawn(notify(  gufi_msg,    advisory_subscriptions_2))
        else:
            gevent.spawn(notify(  gufi_msg,    advisory_subscriptions_3))

    # gevent.spawn(notify(msg))
    return "OK"

#drone 1 advisory view
@app.route("/advisory_view_1")
def advisories_view_1():
    return render_template('drone_1_advisory.html')

#drone 2 advisory view
@app.route("/advisory_view_2")
def advisories_view_2():
    return render_template('drone_2_advisory.html')

#drone 3 advisory view
@app.route("/advisory_view_3")
def advisories_view_3():
    return render_template('drone_3_advisory.html')

#drone 1 advisory "socket"
@app.route("/advisory_drone_1")
def advisory_1():
    def gen():
        q = Queue()
        advisory_subscriptions_1.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            advisory_subscriptions_1.remove(q)
    return Response(gen(), mimetype="text/event-stream")

#drone 2 advisory "socket"
@app.route("/advisory_drone_2")
def advisory_2():
    def gen():
        q = Queue()
        advisory_subscriptions_2.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            advisory_subscriptions_2.remove(q)
    return Response(gen(), mimetype="text/event-stream")

#drone 3 advisory "socket"
@app.route("/advisory_drone_3")
def advisory_3():
    def gen():
        q = Queue()
        advisory_subscriptions_3.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            advisory_subscriptions_3.remove(q)
    return Response(gen(), mimetype="text/event-stream")

def lat_lon_convert(lat, lon):
    lat_offset = lat / 111111.0 * 1.0
    new_lat = base_lat + lat_offset
    lon_offset = lon / 111111.0 * np.cos(new_lat)
    new_lon = base_long + lon_offset
    return new_lat, new_lon

@app.route("/conflict", methods=['POST', 'GET'])
def consume_conflict():
    # #starts at Lake Lagunita for now
    # base_lat = 37.422570
    # base_long = -122.176514
    drone,lat, lon , heading= request.data.split('~')
    lat, lon , heading= float(lat), float(lon), float(heading)
    #convert it to lat meters

    heading = heading / np.pi * 180

    new_lat, new_lon = lat_lon_convert(lat,lon)
    msg = drone + "~" + str(new_lat) + "~" + str(new_lon) + "~" + str(heading)

    # If your displacements aren't too great (less than a few kilometers) and you're not right at the poles, 
    #use the quick and dirty estimate that 111,111 meters (111.111 km) in the y direction is 1 degree (of latitude) 
    #and 111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude).

    def notify():
        for sub in subscriptions[:]:
            sub.put(msg)
    
    gevent.spawn(notify)
    
    return "OK"



@app.route("/conflict_live", methods=['POST', 'GET'])
def consume_conflict_live():
    # #starts at Lake Lagunita for now
    # base_lat = 37.422570
    # base_long = -122.176514
    drone,lat, lon , heading= request.data.split('~')

    if drone == gufi_1:
        drone = "drone1"

    if drone == gufi_2:
        drone = "drone2"

    lat, lon , heading= float(lat), float(lon), float(heading)
    #convert it to lat meters

    heading = heading / np.pi * 180
    # new_lat, new_lon = lat_lon_convert(lat,lon)
    msg = drone + "~" + str(lat) + "~" + str(lon) + "~" + str(heading)

    # If your displacements aren't too great (less than a few kilometers) and you're not right at the poles, 
    #use the quick and dirty estimate that 111,111 meters (111.111 km) in the y direction is 1 degree (of latitude) 
    #and 111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude).

    def notify():
        for sub in subscriptions[:]:
            sub.put(msg)
    
    gevent.spawn(notify)
    
    return "OK"

@app.route("/publish")
def publish():
    #Dummy data - pick up from request for real data
    def notify():
        msg = str(time.time())
        for sub in subscriptions[:]:
            sub.put(msg)
    
    gevent.spawn(notify)
    
    return "OK"

@app.route("/subscribe")
def subscribe():
    def gen():
        q = Queue()
        subscriptions.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            subscriptions.remove(q)

    return Response(gen(), mimetype="text/event-stream")

if __name__ == "__main__":
    print app.root_path
    app.debug = True
    server = WSGIServer(("", 5000), app)
    server.serve_forever()
    # Then visit http://localhost:5000 to subscribe 
    # and send messages by visiting http://localhost:5000/publish