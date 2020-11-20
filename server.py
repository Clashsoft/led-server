from flask import Flask, request, make_response

from wakeonlan import send_magic_packet
from rpi_ws281x import *

import time
import os
import sys

sys.path.append(os.path.abspath('.'))

# Server Configuration
PORT = 8080

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


def colorSet(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


def colorWipe(strip, color, wait_ms=20):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def theaterChase(strip, color, iterations=10, wait_ms=20):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=1):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)


def theaterChaseRainbow(strip, wait_ms=20):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def snake(strip, color=Color(255, 255, 255), wait_ms=20, width=5):
    black = Color(0, 0, 0)
    for i in range(strip.numPixels()):
        for j in range(strip.numPixels()):
            delta = j - i
            strip.setPixelColor(j, color if delta >= 0 and delta < width else black)
        strip.show()
        time.sleep(wait_ms/1000.0)


# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

app = Flask(__name__)

with open('keys.txt') as keyFile:
    keys = set()
    for line in keyFile:
        stripped = line.strip()
        if len(stripped) > 0 and not stripped.startswith('#'):
            keys.add(stripped)


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

    print(key, 'played', body)

    effect = body['effect']
    color = Color(body['r'], body['g'], body['b'])
    if effect == 'set':
        colorSet(strip, color)
    elif effect == 'wipe':
        colorWipe(strip, color)
    elif effect == 'theaterChase':
        theaterChase(strip, color)
    elif effect == 'rainbow':
        rainbow(strip)
    elif effect == 'rainbowCycle':
        rainbowCycle(strip)
    elif effect == 'theaterChaseRainbow':
        theaterChaseRainbow(strip)
    elif effect == 'snake':
        snake(strip, color)
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
