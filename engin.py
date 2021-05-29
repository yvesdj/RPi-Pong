import paho.mqtt.client as mqtt
# import RPi.GPIO as GPIO
from time import sleep
# GPIO.setmode(GPIO.BCM)



class Ball:
   x = 0
   y = 0

   def __init__(self, x, y):
       self.x = x
       self.y = y



#variabelen
broker = "broker.mqttdashboard.com" # "87.67.133.107"
topic = "TeamCL1-4/Pong"
heightL,heightR=10,10
speedL,speedR=1,1
rondes=0
puntenL,puntenR=0,0
puntenLT,puntenRT=0,0
# ballX,ballY=0,0
ball = Ball(390, 410)

#verbinding maken met het topic
def on_connect(client, userdata, flags, rc):
    if rc == 0:
	    print ("Connected succesfully")
    else:
	    print (f"Connection failed with code {rc}")
    client.subscribe(topic)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


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
      client.publish(topic, payload="SRC=ENG; DST=DISPL; RACKET=L; HEIGHT=" + str(heightL) + ";",qos=0)

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
      client.publish(topic, payload="SRC=ENG; DST=DISPL; RACKET=R; HEIGHT=" + str(heightR) + ";",qos=0)

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

   else:
      print("Couldn't resolve message: " + load)

def on_publish(client, userdata, mid):
    print("mid: " + str(mid))

def updateBallPos(ball, refreshTime):
   ball.x += 5
   ball.y += 5

   client.publish(topic, payload="SRC=ENG; DST=DISPL; BALL_X=" + str(ball.x) + "; BALL_Y=" + str(ball.y) + ";")
   
   sleep(refreshTime)



#MQTT instellen
client = mqtt.Client()

#try om het correct af te kunnen afsluiten
try:
   client.on_connect = on_connect
   client.on_subscribe = on_subscribe
   client.on_message = on_message
   client.on_publish = on_publish

   client.connect(broker, 1883)

   client.loop_start()
   # client.loop_forever()

   while(True):
      updateBallPos(ball, 5)

#cleanup
except KeyboardInterrupt: 
    print("\nStopping this script.")
