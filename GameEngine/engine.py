from Model.Player import Player
from Model.Paddle import Paddle
from Model.Ball import Ball
import paho.mqtt.client as mqtt
import random as rnd
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


def on_publish(client, userdata, mid):
    print("mid: " + str(mid))
    

def sendMessage(source:str, destination:str, message:str):
    client.publish(topic, payload="SRC="+source+"; DST="+destination+"; "+message+";",qos=0)



def assignPaddles():
#wijs een random paddle toe aan de spelers
    random = rnd.uniform(0,1)
    if random:
        player1.paddle = paddle1
        player2.paddle = paddle2
    else:
        player1.paddle = paddle2
        player2.paddle = paddle1

    for i,player in enumerate(players,start=1):
        sendMessage("ENG","CTRL"+str(i),"ASSIGNED_RACKET="+player.paddle.side)



def on_message(client, userdata, msg):
#actie bij detecteren van een bericht
    global rounds, speedMax, speedIncrement
    global fieldWidth, fieldHeight
    global newGame

    load = str(msg.payload)
    
    SRCindex = load.find("SRC=CTRL")
    if SRCindex != -1:
        p = int(load[SRCindex+8:SRCindex+9]) - 1
        findInLoadForPlayer(load, players[p])
        sendMessage("ENG","DISPL","RACKET=" + players[p].paddle.side+"; HEIGHT=" + str(players[p].paddle.y))

    #nieuw spel beginnen                    
    elif load.find("MSG=STARTGAME") != -1:
        for player in players:
            player.score = 0
            player.tmpScore = 0
            player.paddle.speed = 5
            player.paddle.y = 10
        rounds = 0
        configMessages = ("RACKET=L; HEIGHT=10","RACKET=L; SCORE=0","RACKET=L; TMPSCR=0","RACKET=L; ","RACKET=R; HEIGHT=10","RACKET=R; SCORE=0","RACKET=R; TMPSCR=0","RACKET=R; ")
        for msg in configMessages:
            sendMessage("ENG","DISPL",msg)
        sendMessage("ENG","ALL","MSG=NEWGAME")
        newGame = True
        
    else:
        print("Couldn't resolve message: " + load)


def findInLoadForPlayer(load: str, player: Player):
#inkomend bericht van een CTRL onderzoeken
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
    global rounds
    #nieuwe ronde starten
    if rounds < 10:
        rounds += 1
        sendMessage("ENG","ALL","MSG=NEWROUND")
        return False
        
    #spel beïndigen
    else:
        sendMessage("ENG","DISPL","MSG=ENDGAME")
        return True


def moveBall(ball, velocityX, velocityY):
    ball.x += velocityX
    ball.y += velocityY


def updateBallPos(ball: Ball, ballSpeed: int, refreshTime:float):
    global fBallGoingDown, fBallGoingRight, fieldHeight, fieldWidth
    vX, vY = 0, 0
    
    goal = "N/A"
    checkCollision(ball)

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
            #TODO kijk na
            #fBallGoingRight = False niet nodig, want de ronde is over
            #goal aan de rechter kant
            goal = "R"

    if fBallGoingRight == False:            
        if ball.x > 0:
            vX = -ballSpeed
        else:
            #TODO kijk na
            #fBallGoingRight = True niet nodig, want de ronde is over
            #goal aan de linker kant
            goal = "L"

    moveBall(ball, vX, vY)
    sendMessage("ENG","DISPL","BALL_X=" + str(ball.x) + "; BALL_Y=" + str(ball.y))
    sleep(refreshTime)
    return goal 

def isBallCollisionWithPaddle(ball: Ball, paddle: Paddle) -> bool:
    topB = ball.y
    bottomB = ball.y + ball.size
    leftB = ball.x
    rightB = ball.x + ball.size

    topP = paddle.y
    bottomP = paddle.y + paddle.height
    leftP = paddle.x
    rightP = paddle.x + paddle.width

    if (topB > bottomP or rightB < leftP or bottomB < topP or leftB > rightP):
        return False
    return True

def checkCollision(ball: Ball):
    global fBallGoingRight
    for player in players:
        print(isBallCollisionWithPaddle(ball, player.paddle))
        if isBallCollisionWithPaddle(ball, player.paddle):
            print("\n\n COLLISION \n\n")
            player.tmpScore += 5
            fBallGoingRight = not fBallGoingRight


if __name__ == "__main__":
    #MQTT instellen
    client = mqtt.Client()
    
    #variabelen
    broker = "broker.mqttdashboard.com" # "87.67.133.107"
    topic = "TeamCL1-4/Pong"
    rounds=0
    speedMax,speedIncrement = 15,5
    fieldWidth, fieldHeight = 800, 600
    paddle1 = Paddle("L", 10, 10, 20, 90, 5, False)
    paddle2 = Paddle("R", 770, 10, 20, 90, 5, False)
    player1 = Player(paddle1, 0, 0)
    player2 = Player(paddle2, 0, 0)
    players = (player1, player2)
    ball = Ball(390, 410, 10)
    fBallGoingDown = True
    fBallGoingRight = True

    newGame = False


    #try om het correct af te kunnen afsluiten
    try:
        client.on_connect = on_connect
        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.on_publish = on_publish
        client.connect(broker, 1883)

        client.loop_start()
        #client.loop_forever()
        endGame = False
        
        #gameloop
        while (True):
            assignPaddles()
            goalSide = "N/A"
            
            #roundloop
            while(goalSide == "N/A"):
                goalSide = updateBallPos(ball, 10, 0.5)

            #goal is gemaakt
            for player in players:
                if player.paddle.side != goalSide:
                    player.score += player.tmpScore
                    sendMessage("ENG","DISPL","RACKET=" + player.paddle.side +"SCORE=" + str(player.score))
                player.tmpScore = 0
                sendMessage("ENG","DISPL","RACKET=" + player.paddle.side + "; " + "TMPSCR=0")
            
            endGame = endRound()
            while (endGame):
                #TODO niet zeker of dit werkt
                #het zou misschien kunnen lukken zonder de if
                #wachten op startgame message van display
                if newGame:
                    endGame = False
            

    #afsluiten
    except KeyboardInterrupt: 
        print("\nGame engine wordt afgesloten.")

