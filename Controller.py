import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
green,yellow,red = 14,15,18
leds = (green,yellow,red)
btns = (17,27,22) #Up, Down, speed

#variabelen
contrlNmbr = "1" #dit is afhankelijk van op welke controller het runt (1 of 2)
broker = "87.67.133.107"
topic = "TeamCL1-4/Pong"

for led in leds:
    GPIO.setup(led, GPIO.OUT, initial=GPIO.LOW)
for btn in btns:
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#verbinding maken met het topic
def on_connect(client, userdata, flags, rc):
    if rc == 0:
	    print ("Connected succesfully")
    else:
	    print (f"Connection failed with code {rc}")
    client.subscribe(topic)

#knipper voor het begin van een ronde
def blink():
    for i in range(3):
        sleep(1)
        GPIO.output(yellow, True)
        sleep(1)
        GPIO.output(yellow, False)

#commando versturen na druk op knop
def callback_SendMessage(channel):
    action = ""
    if channel == btns[0]:
        action = "UP"
    elif channel == btns[1]:
        action = "DN"
    else:
        action = "SP" #SP_UP is SP geworden omdat het de snelheid doet cyclen niet stijgen
    client.publish(topic, payload="SRC=CTRL" + contrlNmbr + "; DST=ENG; ACTION=" + action+";",qos=0)

#actie bij detecteren van een bericht
def on_message(client, userdata, msg):
    load = str(msg.payload)
    if load.find("DST=CTRL" + contrlNmbr) != -1:
        side = "N/A"
        
        if load.find("ASSIGNED_RACKET=L") != -1:
            GPIO.output(green, True)
            GPIO.output(red, False)
            side = "left"
            
        elif load.find("ASSIGNED_RACKET=R") != -1:
            GPIO.output(red, True)
            GPIO.output(green, False)
            side = "right"
            
        print("You control the "+side+" racket")
        return
    
    elif load.find("MSG=NEWROUND") != -1:
        print("Round starting in 3 seconds!")
        blink()
        
    elif load.find("MSG=NEWGAME") != -1:
        print("Game starting in 3 seconds!")
        blink() 

#MQTT instellen
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, 1883,60)

#buttons met hun acties verbinden
for btn in btns:
    GPIO.add_event_detect(btn, GPIO.FALLING, callback=callback_SendMessage, bouncetime=100)

#try om het correct af te kunnen afsluiten
try:
    client.loop_forever()

#cleanup
except KeyboardInterrupt: 
    print("controller disconnected")
    for btn in btns:
        GPIO.remove_event_detect(btn)
    GPIO.cleanup()
