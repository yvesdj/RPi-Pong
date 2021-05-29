from Model.Ball import Ball
import paho.mqtt.client as mqtt
# import RPi.GPIO as GPIO
from time import sleep
# GPIO.setmode(GPIO.BCM)



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
   global heightL, heightR, puntenL, puntenR
   global puntenLT, puntenRT, speedL, speedR
   global rondes, speedMax, speedIncrement
   global fieldWidth, fieldHeight

   load = str(msg.payload)
   if load.find("SRC=CTRL1") != -1:
      if load.find("ACTION=UP") != -1:
          if heightL < 0:
              heightL = 0
      elif load.find("ACTION=DN") != -1:
          if heightL > fieldHeight:
              heightL = fieldHeight
      elif load.find("ACTION=SP") != -1:
          if speedL < speedMax:
              speedL += speedIncrement
          else:
              speedL = speedIncrement
      client.publish(topic, payload="SRC=ENG; DST=DISPL; RACKET=L; HEIGHT=" + str(heightL) + ";",qos=0)

   elif load.find("SRC=CTRL2") != -1:
      if load.find("ACTION=UP") != -1:
          heightR -= speedR
          if heightR < 0:
              heightR = 0
      elif load.find("ACTION=DN") != -1:
          heightR += speedR
          if heightR > fieldHeight:
              heightR = fieldHeight
      elif load.find("ACTION=SP") != -1:
         if speedR < speedMax:
             speedR += speedIncrement
         else:
             speedR = speedIncrement
      client.publish(topic, payload="SRC=ENG; DST=DISPL; RACKET=R; HEIGHT=" + str(heightR) + ";",qos=0)

   else:
      print("Couldn't resolve message: " + load)


def StartNew(winner = "N/A"):
    global rondes
    if winner != "N/A":
        #TODO voeg tmp punten van winner toe aan zijn perm punten
        puntenLT = 0
        puntenRT = 0
        
    if rondes < 10:
        rondes += 1
        #TODO Wijs kant (L/R) toe aan elke conroller
        #TODO Stuur bericht naar controllers en display dat nieuwe ronde begint
        
    else:
        #spel beïndigd
        #TODO stuur bericht naar display dat het spel is Geëindigd
        #TODO wacht op een reply van een display
        puntenL = 0
        puntenR = 0
        puntenLT = 0
        puntenRT = 0
        rondes = 0
        speedR = 1
        speedL = 1
        heightR = 10
        heightL = 10   

def on_publish(client, userdata, mid):
    print("mid: " + str(mid))

def moveBall(ball, velocityX, velocityY):
    ball.x += velocityX
    ball.y += velocityY

def updateBallPos(ball, ballSpeed, refreshTime):
    global fBallGoingDown, fBallGoingRight, fieldHeight, fieldWidth 
    vX, vY = 0, 0

    if fBallGoingDown == True:
        if ball.y < fieldHeight:
            vY = ballSpeed
        else:
            fBallGoingDown = False

    if fBallGoingDown == False:
        if ball.y > 0:
            vY = -ballSpeed
        else:
            fBallGoingDown = True

    if fBallGoingRight == True:
        if ball.x < fieldWidth:
            vX = ballSpeed
        else:
            fBallGoingRight = False

    if fBallGoingRight == False:
        if ball.x > 0:
            vX = -ballSpeed
        else:
            fBallGoingRight = True

    moveBall(ball, vX, vY)

    client.publish(topic, payload="SRC=ENG; DST=DISPL; BALL_X=" + str(ball.x) + "; BALL_Y=" + str(ball.y) + ";")

    sleep(refreshTime)


if __name__ == "__main__":
   #MQTT instellen
   client = mqtt.Client()
   #variabelen
   broker = "broker.mqttdashboard.com" # "87.67.133.107"
   topic = "TeamCL1-4/Pong"
   heightL,heightR=10,10
   speedL,speedR=1,1
   rondes=0
   puntenL,puntenR=0,0
   puntenLT,puntenRT=0,0
   speedMax,speedIncrement = 15,5

   fieldWidth, fieldHeight = 800, 600

   ball = Ball(390, 410, 10)
   fBallGoingDown = True
   fBallGoingRight = True


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
         updateBallPos(ball, 10, 0.5)

   #cleanup
   except KeyboardInterrupt: 
      print("\nStopping this script.")
   
