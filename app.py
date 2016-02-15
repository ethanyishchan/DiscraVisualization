import random, glob, os, uuid, urllib2, time, httplib, urllib, requests, json

from flask_googlemaps import GoogleMaps, Map
from kafka import KafkaConsumer
from pykafka import KafkaClient
from flask import Flask, request,render_template, jsonify, Response
from flask_socketio import SocketIO, emit, send


app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

GoogleMaps(app)


client = KafkaClient("127.0.0.1:9092")  

@app.route("/")
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers={'http://maps.google.com/mapfiles/ms/icons/green-dot.png':[(37.4419, -122.1419)],
                 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png':[(37.4300, -122.1400)]}
    )

    # print os.path.dirname(os.path.realpath(__file__))
    return render_template('example.html', mymap=mymap, sndmap=sndmap, geocode = (0,0))



@socketio.on('my response')
def test_message(message):
    print "hi"
    print "emitting: ", message
    # emit('my response', {'data': message})
    emit('somerandomevent', message)


@socketio.on('connect')
def handle_c_message():
    message = "hi123"
    print 'received message: ' + message
    send(message)
    send('connected')



@app.route('/conflict', methods=['POST', 'GET'])
def consume_conflict():
    error = None
    if request.method == 'POST':
        # print "hi"
        status_update = json.loads(request.data)
        gufi = status_update['flightId']
        lat = status_update['lat']
        lon = status_update['lon']
        speed = status_update['speed']
        heading = status_update['heading']
        

        # return render_template('example.html', geocode=gufi)
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
        
        # print "before"

        message =  (lat,lon)
        print "before: ", message


        test_message(message) 


        print "after"
        return 0 
        # return render_template('example.html', mymap=mymap, sndmap=sndmap, geocode = (lat,lon))
    return 0
    


@app.route('/', methods=['GET', 'POST'])
def parse_request():
    print request.data


if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app)
    app.run(debug=True)