# Python file to make a mqtt publisher and subscriber
# The idea is to have a publisher that publishes a message when a given coordinate is reached 

import paho.mqtt.client as mqtt
import time
import json
import random

y=0
x=0
coordinates = [x,y]

def moving_forward():
    for i in range(0,100):
        coordinates[1] += 1
        time.sleep(0.5)
        print(coordinates)