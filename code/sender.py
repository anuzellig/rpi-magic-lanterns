#!/usr/bin/env python3

# This process watches for button presses, picks the pattern (or off), and publishes it to SNS

import os
import boto3
# from random import randint
import time
import json
from random import randint

# If running in a development environment (no on an RPi) import a fake GPIO lib
if 'DEV' in os.environ:
    from CatchAll import CatchAll
    GPIO = CatchAll()
else:
    # noinspection PyUnresolvedReferences
    import RPi.GPIO as GPIO


def get_button_press():
    timer = None
    while True:
        input_state = GPIO.input(17)
        if input_state:
            if timer:
                duration = time.time() - timer
                if duration > .1:
                    return duration
        else:
            if not timer:
                timer = time.time()
        time.sleep(0.01)


if __name__ == "__main__":
    profile_name = os.environ.get('PROFILE')
    sns_topic = os.environ.get('SNS_TOPIC')
    session = boto3.Session(profile_name=profile_name)
    client = session.client('sns')

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    number_of_patterns = 7  # Including off
    pattern_index = 0

    while True:
        duration = get_button_press()

        if duration > 1:
            # Turn lamp off on a long press
            pattern_index = 0
        else:
            # Cycle through them sequentially
            pattern_index += 1
            if pattern_index > number_of_patterns - 1:
                pattern_index = 1

        if pattern_index == 4:
            # This is the random candle. Pick and communicate the color now so the candles have the same color
            red = randint(0, 255)
            blue = randint(0, 255)
            green = randint(0, 255)
            message = {'pattern_index': pattern_index, 'red': red, 'green': green, 'blue': blue}
        else:
            # Otherwise just send the pattern index
            message = {'pattern_index': pattern_index}

        message_json = json.dumps(message)

        client.publish(Message=message_json, TopicArn=sns_topic)
