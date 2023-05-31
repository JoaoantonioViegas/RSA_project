import paho.mqtt.client as mqtt
import time
import json
import random
from geopy.distance import distance, geodesic
from geopy import Point
import math
from termcolor import colored
import threading

ID=2

def calculate_initial_compass_bearing(pointA, pointB):
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2() returns values from -π to + π
    # So we need to normalize the result, to convert it to a compass bearing as it
    # should be in the range 0° to 360°
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def get_coordinates(lat1, lon1, lat2, lon2, speed):
    start = Point(latitude=lat1, longitude=lon1)
    end = Point(latitude=lat2, longitude=lon2)
    distance = geodesic(start, end).kilometers
    distance_meters = distance * 1000
    speedms = speed * 0.277778
    #how many seconds it takes to travel the distance_meters at speedms
    seconds = distance_meters / speedms
    #how many times the message should be sent per second
    N = 10
    #how many samples to take
    samples = int(seconds * N)
    #step size in meters
    step = distance_meters / samples

    bearing = calculate_initial_compass_bearing((lat1, lon1), (lat2, lon2))

    coordinates = []
    for i in range(samples+1):
        step_distance = step * i
        step_point = geodesic(meters=step_distance).destination(point=start, bearing=bearing)
        #round to only 6 decimal places after the point
        step_point.latitude = round(step_point.latitude, 6)
        step_point.longitude = round(step_point.longitude, 6)
        coordinates.append((step_point.latitude, step_point.longitude))

    return coordinates

def coordinates_to_dict(coordinates):
    return {i+1: (round(coordinate[0], 6), round(coordinate[1], 6)) for i, coordinate in enumerate(coordinates)}

def travel(street_list, speed_list, delay):
    j = 0
    for street in street_list:
        for key, coord in street.items():
            message = construct_message(coord[0], coord[1], speed_list[j])
            publish_message(message)
            print(colored("latitude: " + str(coord[0]) + " longitude: " + str(coord[1]) + " speed: " + str(speed_list[j]) +" km/h","green"))
            time.sleep(delay)
        j += 1
        print("\n")


client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
client.connect("192.168.98.12", 1883, 60)

threading.Thread(target=client.loop_forever).start()

# create a function that will publish the message to the broker mosquitto_pub -h 192.168.98.1 -t "vanetza/in/cam" -m "message"
def publish_message(message):
    client.publish("vanetza/in/cam", message)


def construct_message(latitude,longtitude, speed):
    f = open('./in_cam.json')
    m = json.load(f)
    m["latitude"] = latitude
    m["longitude"] = longtitude
    m["speed"] = speed
    m["stationID"] = ID
    m = json.dumps(m)
    return m

# street = [(start.x, start.y), (end.x, end.y)]

A25_1 = [(40.636800, -8.667729),(40.639178, -8.664639),100]
A25_2 = [(40.639178, -8.664639),(40.642825, -8.659768),110]
A25_3 = [(40.642825, -8.659768),(40.646065, -8.654425),120]
A25_4 = [(40.646065, -8.654425),(40.648198, -8.650198),110]
A25_5 = [(40.648198, -8.650198),(40.650509, -8.646250),120]

A25_1_street = coordinates_to_dict(get_coordinates(A25_1[0][0], A25_1[0][1], A25_1[1][0], A25_1[1][1], A25_1[2]))
A25_2_street = coordinates_to_dict(get_coordinates(A25_2[0][0], A25_2[0][1], A25_2[1][0], A25_2[1][1], A25_2[2]))
A25_3_street = coordinates_to_dict(get_coordinates(A25_3[0][0], A25_3[0][1], A25_3[1][0], A25_3[1][1], A25_3[2]))
A25_4_street = coordinates_to_dict(get_coordinates(A25_4[0][0], A25_4[0][1], A25_4[1][0], A25_4[1][1], A25_4[2]))
A25_5_street = coordinates_to_dict(get_coordinates(A25_5[0][0], A25_5[0][1], A25_5[1][0], A25_5[1][1], A25_5[2]))

def main():
    path = [A25_1_street, A25_2_street, A25_3_street, A25_4_street]
    speed = [100, 110, 120, 110]
    while True:
        travel(path, speed, 0.1)

if __name__ == "__main__":
    main()