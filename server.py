import os
import sys

sys.path.append(os.path.abspath('.'))

from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy

import json

import animations
import push
from rpi_ws281x_wrapper import Adafruit_NeoPixel

# LED strip configuration:
LED_COUNT = 300      # Number of LED pixels.
LED_PIN = 18      # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

app = Flask(__name__)

with open('keys.txt') as keyFile:
    keys = dict()
    for line in keyFile:
        stripped = line.strip()
        if len(stripped) > 0 and not stripped.startswith('#'):
            key, name = stripped.split(None, 1)
            keys[key] = name


# --------------- Database ---------------

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class PushSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    token = db.Column(db.Text, nullable=False)


db.create_all()


# --------------- Endpoints ---------------

@app.route('/api/subscriptions', methods=['OPTIONS', 'POST'])
def subscription():
    if request.method == 'OPTIONS':
        return options()

    if keys[request.headers['X-LED-Key']] != 'Admin':
        return {'error': 'invalid key'}, 401

    body = request.json
    subscription_info = body['subscriptionInfo']
    subscription = PushSubscription(token=json.dumps(subscription_info))
    db.session.add(subscription)
    db.session.commit()
    return {'id': subscription.id}


@app.route('/api/effects', methods=['OPTIONS', 'GET'])
def get_effects():
    if request.method == 'OPTIONS':
        return options()

    return {id: {'name': effect.name, 'description': effect.description} for id, effect in animations.effects.items()}


@app.route('/api/effect', methods=['POST', 'OPTIONS'])
def set_color():
    if request.method == 'OPTIONS':
        return options()

    key = request.headers['X-LED-Key']
    if key not in keys:
        return {
            'error': 'invalid key',
        }, 401

    body = request.json

    print(key, keys[key], 'played', body)

    effect = body['effect']
    color = animations.Color(body['r'], body['g'], body['b'])
    effect = animations.effects.get(effect)
    if effect is None:
        return {'error': 'unknown effect'}, 404

    effect.method(strip, color)

    notification = {
        'notification': {
            'title': 'LED Server',
            'body': keys[key] + ': ' + body.get('message', ''),
        }
    }
    for subscription in PushSubscription.query.all():
        push.send_web_push(json.loads(subscription.token), notification)

    return {}


def options():
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    return response


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
