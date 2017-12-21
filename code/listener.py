#!/usr/bin/env python3

# This process does long polling of this lantern's SQS queue and sets the led pattern accordingly
# The code that lights the lights will have to be a seperate process or thread or something

import os
import boto3
import threading
import time
import json
import subprocess

from patterns import light_rainbow, candle, red_candle, random_candle, insane, blink_random

# If running in a development environment (no on an RPi) import a fake unicornhat lib
if 'DEV' in os.environ:
    from CatchAll import CatchAll
    uh = CatchAll()
else:
    # noinspection PyUnresolvedReferences
    import unicornhat as uh

uh.set_layout(uh.PHAT)
uh.brightness(1)


class LightThread(threading.Thread):
    def __init__(self, thread_id, index, red=None, green=None, blue=None):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.index = index
        self.do_run = True
        self.exited = False
        self.red = red
        self.green = green
        self.blue = blue

    def run(self):
        light_the_lights(self.index)


def light_the_lights(index):
    global lighting_functions
    func = lighting_functions[index]
    t = threading.currentThread()
    func(t)
    t.exited = True


def light_off(t):
    _ = t
    uh.clear()
    uh.show()


def check_if_functional():
    # Test to see if we have internet access. If so flash green. Otherwise flash red
    try:
        subprocess.check_output('ping -c 1 -w 1 www.amazon.com', shell=True)
        print('Functional')
        # Internet access functional. Flash green.
        for x in range(8):
            for y in range(4):
                uh.set_pixel(x, y, 0, 255, 0)
        uh.show()
        time.sleep(0.25)
        uh.clear()
        uh.show()

    except subprocess.CalledProcessError:
        print('Not functional')
        # Ping failed. Blink Red
        for _ in range(0, 25):
            for x in range(8):
                for y in range(4):
                    uh.set_pixel(x, y, 255, 0, 0)
            uh.show()
            time.sleep(0.2)
            uh.clear()
            uh.show()
            time.sleep(0.2)


if __name__ == "__main__":
    sqs_queue_url = os.environ.get('SQS_QUEUE_URL')
    thread = None
    message_json = None
    index = 0
    lighting_functions = (light_off, light_rainbow, candle, red_candle, random_candle, insane, blink_random)

    check_if_functional()

    profile_name = os.environ.get('PROFILE')
    session = boto3.Session(profile_name=profile_name)
    client = session.client('sqs')
    while True:
        messages = client.receive_message(QueueUrl=sqs_queue_url, MaxNumberOfMessages=10)
        if 'Messages' in messages:  # when the queue is exhausted, the response dict contains no 'Messages' key
            # We only care about the last message, so just consume them all
            for message in messages['Messages']:
                # process the messages
                message_json = json.loads(message['Body'])['Message']
                client.delete_message(QueueUrl=sqs_queue_url, ReceiptHandle=message['ReceiptHandle'])

            message_dict = json.loads(message_json)
            index = int(message_dict['pattern_index'])

            # Spin up a thread to handle the lights
            if thread:
                thread.do_run = False
                while not thread.exited:
                    time.sleep(0.01)
            if index == 4:
                # If this is the random candle, get the color
                red = message_dict['red']
                green = message_dict['green']
                blue = message_dict['blue']
                thread = LightThread(1, index, red, green, blue)
            else:
                thread = LightThread(1, index)
            thread.start()
