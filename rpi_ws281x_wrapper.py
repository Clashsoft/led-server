try:
    import rpi_ws281x

    Color = rpi_ws281x.Color
    Adafruit_NeoPixel = rpi_ws281x.Adafruit_NeoPixel
except ImportError:
    class Color:
        def __init__(self, r, g, b):
            self.r = r
            self.g = g
            self.b = b


    class Adafruit_NeoPixel:
        def __init__(self, led_count, *_):
            self.led_count = led_count

        def begin(self):
            pass

        def numPixels(self):
            return self.led_count

        def setPixelColor(self, index, color):
            pass

        def show(self):
            pass
