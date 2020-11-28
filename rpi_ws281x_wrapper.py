try:
    import rpi_ws281x

    Color = rpi_ws281x.Color
    Adafruit_NeoPixel = rpi_ws281x.Adafruit_NeoPixel
except ImportError:
    def Color(red, green, blue, white=0):
        return (white << 24) | (red << 16) | (green << 8) | blue


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
