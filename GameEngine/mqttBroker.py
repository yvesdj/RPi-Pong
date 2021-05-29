#!/usr/bin/python
# import RPi.GPIO as GPIO
import time as Time
import paho.mqtt.client as mqtt
import re

# GPIO.setmode(GPIO.BCM)

# clientId = "clientId-rNWNvaz5qY"
topic = "TeamCL1-4/Pong"
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(topic)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    print(str(msg.payload))

def on_publish(client, userdata, mid):
    print("mid: " + str(mid))



try:

    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish

    client.connect("87.67.133.107", 1883)

    client.loop_start()
    # client.loop_forever()
    
    while (True):
        Time.sleep(2)
        client.publish(topic, payload="test",qos=0)



except KeyboardInterrupt:
    print("\nStopping this script.")

except:
    print("Something went wrong.")

# finally:
#     # GPIO.cleanup()