import os
import sys

sys.path.append(os.path.abspath('.'))

from flask import Flask, request, make_response

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


subscriptions = []


@app.route('/api/subscriptions', methods=['OPTIONS', 'POST'])
def subscription():
    if request.method == 'OPTIONS':
        return options()

    if keys[request.headers['X-LED-Key']] != 'Admin':
        return {'error': 'invalid key'}, 401

    body = request.json
    subscription_info = body['subscriptionInfo']
    subscriptions.append(subscription_info)
    return {}


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

    for subscription in subscriptions:
        push.send_web_push(subscription, {
            'notification': {
                'title': 'LED Server',
                'body': keys[key] + ': ' + body.message,
            }
        })

    effect = body['effect']
    color = animations.Color(body['r'], body['g'], body['b'])
    if effect == 'set' or effect == 'fill':
        animations.fill(strip, color)
    elif effect == 'wipe':
        animations.wipe(strip, color)
    elif effect == 'theaterChase':
        animations.theaterChase(strip, color)
    elif effect == 'rainbow':
        animations.rainbow(strip)
    elif effect == 'rainbowCycle':
        animations.rainbowCycle(strip)
    elif effect == 'theaterChaseRainbow':
        animations.theaterChaseRainbow(strip)
    elif effect == 'snake':
        animations.snake(strip, color)
    else:
        return {
            'error': 'unknown effect',
        }

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
