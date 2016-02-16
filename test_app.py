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

    return render_template('map2.html', mymap = mymap, sndmap = sndmap)

@app.route("/debug")
def debug():
    return "Currently %d subscriptions" % len(subscriptions)

@app.route("/conflict", methods=['POST', 'GET'])
def consume_conflict():
    #Dummy data - pick up from request for real data
    status_update = json.loads(request.data)
    gufi = status_update['flightId']
    lat = status_update['lat']
    lon = status_update['lon']
    speed = status_update['speed']
    heading = status_update['heading']
    msg =  (lat,lon)

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