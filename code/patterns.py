#!/usr/bin/env python3

# The patterns used by the listener

import time
import colorsys
from random import randint, random
import os

# If running in a development environment (no on an RPi) import a fake unicornhat lib
if 'DEV' in os.environ:
    from CatchAll import CatchAll
    uh = CatchAll()
else:
    # noinspection PyUnresolvedReferences
    import unicornhat as uh


def light_rainbow(t):
    spacing = 360.0 / 16.0

    while getattr(t, 'do_run', True):
        hue = int(time.time() * 100) % 360
        for x in range(8):
            offset = x * spacing
            h = ((hue + offset) % 360) / 360.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
            for y in range(4):
                uh.set_pixel(x, y, r, g, b)
        uh.show()
        time.sleep(0.05)


def blink_random(t):
    while getattr(t, 'do_run', True):
        red = randint(0, 255)
        green = randint(0, 255)
        blue = randint(0, 255)

        for x in range(8):
            for y in range(4):
                uh.set_pixel(x, y, red, green, blue)

        uh.show()
        time.sleep(0.25)


def insane(t):
    while getattr(t, 'do_run', True):
        red = randint(0, 255)
        blue = randint(0, 255)
        green = randint(0, 255)

        for x in range(8):
            for y in range(4):
                uh.set_pixel(x, y, red, green, blue)

        uh.show()


def candle(t):
    random_candle(t, red=255, green=180, blue=70)


def red_candle(t):
    random_candle(t, red=255, green=0, blue=0)


def random_candle(t, red=None, green=None, blue=None):
    if red is None:
        red = getattr(t, 'red')
    if green is None:
        green = getattr(t, 'green')
    if blue is None:
        blue = getattr(t, 'blue')

    def light_on():
        for x in range(8):
            for y in range(4):
                uh.set_pixel(x, y, red, green, blue)
        uh.show()

    def go_to_brightness(current, new):
        if current is None:
            uh.brightness(new / 100)
            light_on()
            return new

        if current > new:
            step = -1
        else:
            step = 1
        for b in range(current, new, step):
            uh.brightness(b / 100)
            light_on()
        return new

    breeze = 6
    old_brightness = None
    while getattr(t, 'do_run', True):
        brightness = randint(30, 100)
        flicker = random() / breeze
        old_brightness = go_to_brightness(old_brightness, brightness)
        time.sleep(flicker)
