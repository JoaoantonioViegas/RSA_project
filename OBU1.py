# Python file to make a mqtt publisher and subscriber
# The idea is to have a publisher that publishes a message when a given coordinate is reached 

import paho.mqtt.client as mqtt
import time
import json
import random
from geopy.distance import distance

# create a class car that has which atributtes are the coordinates of the car
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y


coordinates = {
    "coord1": (40.636878, -8.647755),
    "coord2": (40.636857, -8.647739),
    "coord3": (40.636804, -8.647680),
    "coord4": (40.636804, -8.647680),
    "coord5": (40.636772, -8.647631),
    "coord6": (40.636723, -8.647588),
    "coord7": (40.636701, -8.647553),
    "coord8": (40.636672, -8.647512),
    "coord9": (40.636646, -8.647475),
    "coord10": (40.636594, -8.647411),
    "coord11": (40.636559, -8.647372),
    "coord12": (40.636522, -8.647324),
    "coord13": (40.636501, -8.647295),
    "coord14": (40.636456, -8.647244),
    "coord15": (40.636426, -8.647212),
    "coord16": (40.636399, -8.647177),
    "coord17": (40.636371, -8.647142),
    "coord18": (40.636340, -8.647113),
    "coord19": (40.636306, -8.647078),
    "coord20": (40.636275, -8.647038),
    "coord21": (40.636240, -8.646997),
    "coord22": (40.636214, -8.646960),
    "coord23": (40.636188, -8.646933),
    "coord24": (40.636157, -8.646895),
    "coord25": (40.636131, -8.646863),
    "coord26": (40.636098, -8.646834),
    "coord27": (40.636074, -8.646799),
    "coord28": (40.636041, -8.646756),
    "coord29": (40.636021, -8.646713),
    "coord30": (40.635994, -8.646686),
    "coord31": (40.635974, -8.646654),
    "coord32": (40.635920, -8.646595),
    "coord33": (40.635885, -8.646552),
    "coord34": (40.635851, -8.646504),
    "coord35": (40.635814, -8.646456),
    "coord36": (40.635771, -8.646394),
}




# make a function that modifies the coordinates of the car
def move_car_forward():
    car.y += 1
    time.sleep(0.1)
        
def construct_message(latitude,longtitude):
    # create a message that will be sent to the broker
    message = {
    "accEngaged": True,
    "acceleration": 0,
    "altitude": 800001,
    "altitudeConf": 15,
    "brakePedal": True,
    "collisionWarning": True,
    "cruiseControl": True,
    "curvature": 1023,
    "driveDirection": "FORWARD",
    "emergencyBrake": True,
    "gasPedal": False,
    "heading": 3601,
    "headingConf": 127,
    "latitude": latitude,
    "length": 10,
    "longitude": longtitude,
    "semiMajorConf": 4095,
    "semiMajorOrient": 3601,
    "semiMinorConf": 4095,
    "specialVehicle": {
        "publicTransportContainer": {
            "embarkationStatus": False
        }
    },
    "speed": 16383,
    "speedConf": 127,
    "speedLimiter": True,
    "stationID": 1,
    "stationType": 15,
    "width": 3,
    "yawRate": 0
    }
    message = json.dumps(message)
    return message


# create a function that will publish the message to the broker mosquitto_pub -h 192.168.98.20 -t "vanetza/in/cam" -m "message"
def publish_message(message):
    client = mqtt.Client()
    client.connect("192.168.98.20", 1883, 60)
    client.publish("vanetza/in/cam", message)
    client.disconnect()

car = Car(0, 0)

# create a main function that will run the program
def main():
    print("Starting RSU1")
    # in a for cycle, print the coordX where X is the iteration of the for cycle
    for i in range(1, 37): 
        # pass throught the message function the coordinates of the car
        message = construct_message(coordinates["coord" + str(i)][0], coordinates["coord" + str(i)][1])
        # publish the message
        publish_message(message)
        # wait 0.1 seconds
        time.sleep(0.2)


if __name__ == "__main__":
    main()





