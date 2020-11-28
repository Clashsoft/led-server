import time

from rpi_ws281x_wrapper import Color


def fill(strip, color):
    """Set color for all pixels at once."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


def wipe(strip, color, wait_ms=20):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, iterations=10, wait_ms=20):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


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


def rainbow(strip, _, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, _, wait_ms=20, iterations=1):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, _, wait_ms=20):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def snake(strip, color=Color(255, 255, 255), wait_ms=20, width=5):
    """A few pixels light up and move across the strip."""
    black = Color(0, 0, 0)
    for i in range(strip.numPixels()):
        for j in range(strip.numPixels()):
            delta = j - i
            strip.setPixelColor(j, color if delta >= 0 and delta < width else black)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def christmas(strip, color=Color(255, 0, 0)):
    """
    Alternates between the color and an shifted version of it
    (red becomes green, green becomes blue, blue becomes red).
    """
    shifted = ((color >> 8) | (color << 16)) & 0xffffff
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color if i % 2 == 0 else shifted)
    strip.show()


class Effect:
    def __init__(self, name, method):
        self.name = name
        self.method = method
        self.description = method.__doc__


effects = {
    'fill': Effect('Fill', fill),
    'wipe': Effect('Wipe', wipe),
    'theaterChase': Effect('Theater Chase', theaterChase),
    'rainbow': Effect('Rainbow', rainbow),
    'rainbowCycle': Effect('Rainbow Cycle', rainbowCycle),
    'theaterChaseRainbow': Effect('Theater Chase Rainbow', theaterChaseRainbow),
    'snake': Effect('Snake', snake),
    'christmas': Effect('Christmas Lights', christmas),
}
