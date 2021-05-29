import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

#variabelen
broker = "broker.mqttdashboard.com"
topic = "TeamCL1-4/Pong"
heightL,heightR=10,10
speedL,speedR=1,1
rondes=0
puntenL,puntenR=0,0
puntenLT,puntenRT=0,0
ballX,ballY=0,0

#verbinding maken met het topic
def on_connect(client, userdata, flags, rc):
    if rc == 0:
	    print ("Connected succesfully")
    else:
	    print (f"Connection failed with code {rc}")
    client.subscribe(topic)
#actie bij detecteren van een bericht

def on_message(client, userdata, msg):
   global heightL, heightR, puntenL, puntenR, puntenLT, puntenRT, speedL, speedR, rondes

   load = str(msg.payload)
   if load.find("SRC=CTRL1") != -1:
      if load.find("ACTION=UP") != -1:
         if heightL < 600:
            heightL -= speedL
      elif load.find("ACTION=DN") != -1:
         if heightL > 1:
            heightL += speedL
      elif load.find("ACTION=SP") != -1:
         if speedL != 3:
            speedL += 1
      else:
         speedL =1
      client.publish(topic, payload="SRC=ENG; DST=DISPL; RACKET=L; HEIGHT=" + heightL + ";",qos=0)

   elif load.find("SRC=CTRL2") != -1:
      if load.find("ACTION=UP") != -1:
         if heightR < 600:
            heightR -= speedR
      elif load.find("ACTION=DN") != -1:
         if heightR > 1:
            heightR += speedR
      elif load.find("ACTION=SP") != -1:
         if speedR != 3:
            speedR += 1
      else:
         speedR = 1
      client.publish(topic, payload="SRC=ENG; DST=DISPL; RACKET=R; HEIGHT=" + heightR + ";",qos=0)

   elif load.find("MSG=NEWROUND") != -1:
      if puntenL > puntenR:
         puntenLT += puntenL
         puntenL = 0
         puntenR = 0
      else:
         puntenRT += puntenR
         puntenR = 0
         puntenL = 0
      rondes += 1
   elif load.find("MSG=NEWGAME") != -1:
      puntenL = 0
      puntenR = 0
      puntenLT = 0
      puntenRT = 0
      rondes = 0
      speedR = 1
      speedL = 1
      heightR = 10
      heightL = 10

#MQTT instellen
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, 1883)

#try om het correct af te kunnen afsluiten
try:
    client.loop_forever()

#cleanup
except KeyboardInterrupt: 
    print("\nStopping this script.")
