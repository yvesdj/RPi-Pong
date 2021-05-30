from Model.Player import Player
from Model.Paddle import Paddle
from Model.Ball import Ball
import paho.mqtt.client as mqtt
import random
from time import sleep



#verbinding maken met het topic
def on_connect(client, userdata, flags, rc):
    if rc == 0:
	    print ("Connected succesfully")
    else:
	    print (f"Connection failed with code {rc}")
    client.subscribe(topic)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def sendMessage(source:str, destination:str, message:str):
    client.publish(topic, payload="SRC="+source+"; DST="+destination+"; "+message+";",qos=0)

#wijs een random paddle toe aan de spelers
def assignPaddles():
        random = random.randint(0,1)
        if random:
            player1.paddle = paddle1
            player2.paddle = paddle2
        else:
            player1.paddle = paddle2
            player2.paddle = paddle1

        for i,player in enumerate(players,start=1):
            sendMessage("ENG","CTRL"+str(i),"ASSIGNED_RACKET="+player.paddle.side)

#actie bij detecteren van een bericht
def on_message(client, userdata, msg):
    global player1, player2
    global rondes, speedMax, speedIncrement
    global fieldWidth, fieldHeight

    load = str(msg.payload)
    
    SRCindex = load.find("SRC=CTRL")
    if SRCindex != -1:
        p = load[SRCindex+8:SRCindex+9]
        findInLoadForPlayer(load, players[p])
        sendMessage("ENG","DISP","RACKET="+players[p].paddle.side+"; HEIGHT=" + str(players[p].paddle.y))

    #nieuw spel beginnen                    
    elif load.find("MSG=STARTGAME") != -1:
        for player in players:
            player.score = 0
            player.tmpScore = 0
            player.paddle.speed = 5
            player.paddle.y = 10
        rondes = 0
        configMessages("RACKET=L; HEIGHT=10","RACKET=L; SCORE=0","RACKET=L; TMPSCR=0","RACKET=L; ","RACKET=R; HEIGHT=10","RACKET=R; SCORE=0","RACKET=R; TMPSCR=0","RACKET=R; ")
        for msg in configMessages:
            sendMessage("ENG","DISP",msg)
        sendMessage("ENG","ALL","MSG=NEWGAME")
        
    else:
        print("Couldn't resolve message: " + load)


def findInLoadForPlayer(load: str, player: Player):
    if load.find("ACTION=UP") != -1:
        if player.paddle.y > 0:
            player.paddle.y -= player.paddle.speed
        else:
            player.paddle.y = 0

    elif load.find("ACTION=DN") != -1:
        if player.paddle.y < fieldHeight:
            player.paddle.y += player.paddle.speed
        else:
            player.paddle.y = fieldHeight

    elif load.find("ACTION=SP") != -1:
        print(player.paddle.decrementSpeed)
        if player.paddle.speed < speedMax and not player.paddle.decrementSpeed:
            player.paddle.speed += speedIncrement
            print("player 1 speed increased to: " + str(player.paddle.speed))

        elif player.paddle.speed > speedMax and not player.paddle.decrementSpeed:
            player.paddle.speed = speedMax
            player.paddle.decrementSpeed = True

        elif player.paddle.speed > 5 and player.paddle.decrementSpeed:
            player.paddle.speed -= speedIncrement
            print("player 1 speed decreased to: " + str(player.paddle.speed))

        else:
            player.paddle.speed = 5
            player.paddle.decrementSpeed = False
            
    else:
        print("Couldn't resolve message: " + load)


def endRound():
    global rondes

    #nieuwe ronde starten
    if rondes < 10:
        rondes += 1
        #TODO assign paddle
        sendMessage("ENG","ALL","MSG=NEWROUND")
        return False
        
    #spel beïndigen
    else:
        sendMessage("ENG","DISPL","MSG=ENDGAME")
        return True

def on_publish(client, userdata, mid):
    print("mid: " + str(mid))

def moveBall(ball, velocityX, velocityY):
    ball.x += velocityX
    ball.y += velocityY

def updateBallPos(ball: Ball, ballSpeed: int, refreshTime:float):
    global fBallGoingDown, fBallGoingRight, fieldHeight, fieldWidth 
    vX, vY = 0, 0

    if fBallGoingDown == True:
        if ball.y < fieldHeight - ball.size:
            vY = ballSpeed
        else:
            fBallGoingDown = False

    if fBallGoingDown == False:
        if ball.y > 0:
            vY = -ballSpeed
        else:
            fBallGoingDown = True

    if fBallGoingRight == True:
        if ball.x < fieldWidth - ball.size:
            vX = ballSpeed
        else:
            fBallGoingRight = False

    if fBallGoingRight == False:
        if ball.x > 0:
            vX = -ballSpeed
        else:
            fBallGoingRight = True

    moveBall(ball, vX, vY)

    sendMessage("ENG","DISPL","BALL_X=" + str(ball.x) + "; BALL_Y=" + str(ball.y))

    goalside = "N/A"

    #TODO kijk na of er een punt wordt gescoord en stuur "L" of "R" door voor de kant waar de goal gescoord is
    if false:
        goalside = "L"
        goalside = "R"
        
    sleep(refreshTime)
    return goalside 


if __name__ == "__main__":
    #MQTT instellen
    client = mqtt.Client()
    #variabelen
    broker = "broker.mqttdashboard.com" # "87.67.133.107"
    topic = "TeamCL1-4/Pong"

    rondes=0

    speedMax,speedIncrement = 15,5

    fieldWidth, fieldHeight = 800, 600

    paddle1 = Paddle("L", 10, 10, 20, 90, 5, False)
    paddle2 = Paddle("R", 770, 10, 20, 90, 5, False)

    player1 = Player(paddle1, 0)
    player2 = Player(paddle2, 0)
    players = (player1, player2)

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
        
        endGame = False
        while (!endGame):
            assignPaddles()
            goalSide = "N/A"
            while(goalSide == "N/A"):
                goalSide = updateBallPos(ball, 10, 0.5)
        
            for player in players:
                if player.paddle.side != goalSide:
                    player.score += player.tmpScore
                    sendMessage("ENG","DISP","RACKET="+player.paddle.side+"SCORE="+player.score)
                player.tmpScore = 0
                sendMessage("ENG","DISP","RACKET="+player.paddle.side+"TMPSCR=0")
            
            endGame = endRound()
            

    #cleanup
    except KeyboardInterrupt: 
        print("\nGame engine wordt afgesloten.")

