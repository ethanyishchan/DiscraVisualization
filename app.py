import random, glob, os, uuid, urllib2, time, httplib, urllib, requests, json

from flask_googlemaps import GoogleMaps, Map
from kafka import KafkaConsumer
from pykafka import KafkaClient
from flask import Flask, request,render_template, jsonify, Response, session
from flask.ext.cache import Cache
# from flask_socketio import SocketIO, emit, send
# from uwsgidecorators import *
# from gevent.queue import Queue
# import redis
# from juggernaut import Juggernaut
# from uwsgidecorators import *
# from gevent.queue import Queue
# from gevent import monkey
# monkey.patch_all()

# red = redis.StrictRedis()
# red = redis.Redis("localhost")
# print rs
# red = 

# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)
# jug = Juggernaut()

print "hi"


app = Flask(__name__)
GoogleMaps(app)
client = KafkaClient("127.0.0.1:9092")  
db = redis.Redis('localhost')


@app.route("/")
def mapview():
    # creating a map in the view
    session['cache_logs'] = '0'
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




@app.route('/test_poll', methods=['POST', 'GET'])
def poll():
    print "polled"
    if request.method == 'POST':
        # print request
        rtn_logs = session['cache_logs'] 
        session['cache_logs']  = []
        return rtn_logs

    rtn_logs = session['cache_logs'] 
    session['cache_logs']  = []
    return rtn_logs


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

        # red.publish('chat', str(message))
        # test_message(message) 
        # emit('my response', {'data': 'server Connected'}, broadcast = True)
        print "after"
        # return Response(event_stream(),mimetype="text/event-stream")
        log = status_update, gufi, lat, lon, speed, heading
        cache_logs.append(log)
        return render_template('example.html', mymap=mymap, sndmap=sndmap, geocode = (lat,lon))
    return 0
    
# channels = []

# @filemon('/tmp',target='workers')
# def trigger_event(signum):
#     for channel in channels:
#         try:
#             channel.put_nowait(True)
#         except:
#             pass

# def application(e, sr):
#     sr('200 OK', [('Content-Type','text/html')])
#     yield "Hello and wait..."
#     q = Queue()
#     channels.append(q)
#     q.get()
#     yield "event received, goodbye"
#     channels.remove(q)



# def event_stream():
#     pubsub = red.pubsub()
#     pubsub.subscribe('chat')
#     for message in pubsub.listen():
#         print message
#         # yield 'data: %s\n\n' % message['data']


# @app.route('/post', methods=['POST'])
# def post():
#     message = flask.request.form['message']
#     user = flask.session.get('user', 'anonymous')
#     now = datetime.datetime.now().replace(microsecond=0).time()
#     red.publish('chat', u'[%s] %s: %s' % (now.isoformat(), user, message))


# @app.route('/stream')
# def stream():
#     return Response(event_stream(), mimetype="text/event-stream")




# @socketio.on('my response')
# def test_message(message):
#     print "emitting: ", message
#     # emit('my response', {'data': message})
#     emit('somerandomevent', message)

# @socketio.on('my event')
# def test_event(message):
#     print "receiving my event: ", message


# @socketio.on('connect')
# def handle_c_message():
#     message = "something connected"
#     print 'received message: ' + message
#     emit('my response', {'data': 'server Connected'})

# @app.route('/', methods=['GET', 'POST'])
# def parse_request():
#     print request.data


if __name__ == "__main__":
    # app.run(debug=True)
    # socketio.run(app)
    app.secret_key = '1234'
    app.run(debug=True)

# if __name__ == '__main__':
#     app.debug = True
#     app.run(threaded=True)