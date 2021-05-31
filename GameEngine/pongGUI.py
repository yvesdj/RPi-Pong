from Model.Player import Player
from Model.Paddle import Paddle
from Model.Ball import Ball
from tkinter import *
import paho.mqtt.client as mqtt



def extractStrValueFromString(message: str, searchVar: str, endNotation: str) -> str:
    if message.find(searchVar) != -1:
        start = message.find(searchVar)
        end = message[start:].find(endNotation)

        return message[start + len(searchVar) : start + end]
    else:
        return "0"

# def getPlayerTempScore(player: Player, message: str):
#     player.tmpScore = int(extractStrValueFromString(message, "TMPSCR=", ";"))

def getBallPos(ball: Ball, message: str):
    ball.x = int(extractStrValueFromString(message, "BALL_X=", ";"))
    ball.y = int(extractStrValueFromString(message, "BALL_Y=", ";"))

def getPaddlePos(paddle: Paddle, message: str):
    paddle.y = int(extractStrValueFromString(message, "HEIGHT=", ";"))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(topic)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    load = str(msg.payload)
    print("Payload: " + load)
    if load.find("DST=DISPL") != -1:
        if load.find("BALL") != -1:
            global ball
            getBallPos(ball, load)
            # print(result)
        elif load.find("RACKET") != -1:
            if extractStrValueFromString(load, "RACKET=", ";") == "L":
                if load.find("HEIGHT") != -1:
                    getPaddlePos(player1.paddle, load)
                elif load.find("TMPSCR") != -1:
                    player1.tmpScore = int(extractStrValueFromString(load, "TMPSCR=", ";"))
                elif load.find("SCORE") != -1:
                    player1.score = int(extractStrValueFromString(load, "SCORE=", ";"))
                
            elif extractStrValueFromString(load, "RACKET=", ";") == "R":
                if load.find("HEIGHT") != -1:
                    getPaddlePos(player2.paddle, load)
                elif load.find("TMPSCR") != -1:
                    player2.tmpScore = int(extractStrValueFromString(load, "TMPSCR=", ";"))
                elif load.find("SCORE") != -1:
                    player2.score = int(extractStrValueFromString(load, "SCORE=", ";"))
            else:
                print("Undefined Racket.")
            
            print(str(player1.paddle.y) + "\n" + str(player2.paddle.y))
    elif load.find("DST=ALL") != 1:
        if load.find("MSG=NEWROUND") != 1:
            global round
            print("\n\n AddingRound \n\n")
            round += 1






    else:
        print("Not for me.")

def on_publish(client, userdata, mid):
    print("mid: " + str(mid))





def startRound():
    client.publish(topic, payload="SRC=DISPL; DST=ENG; MSG=STARTGAME;", qos=0)

def updateRound(canvas: Canvas, roundId):
    canvas.itemconfigure(roundId, text=round)

    canvas.after(1000, updateRound, canvas, roundId)

def updatePlayerScore(canvas: Canvas, player: Player, scoreID, tmpScoreID):
    canvas.itemconfigure(scoreID, text=player.score)
    canvas.itemconfigure(tmpScoreID, text=player.tmpScore)

    canvas.after(1000, updatePlayerScore, canvas, player, scoreID, tmpScoreID)

def updateBallPos(canvas: Canvas, ballTexture):
    canvas.coords(ballTexture, ball.x, ball.y, ball.x + ball.size, ball.y + ball.size)

    canvas.after(100, updateBallPos, canvas, ballTexture)

def updatePaddlesPos(canvas: Canvas, paddleTexture, paddleTexture2):
    canvas.coords(paddleTexture, player1.paddle.x, player1.paddle.y, player1.paddle.x + player1.paddle.width, player1.paddle.y + player1.paddle.height)
    canvas.coords(paddleTexture2, player2.paddle.x, player2.paddle.y, player2.paddle.x + player2.paddle.width, player2.paddle.y + player2.paddle.height)

    canvas.after(100, updatePaddlesPos, canvas, paddleTexture, paddleTexture2)

def clearScreen():
    global wFrame, window
    wFrame.destroy()
    wFrame = Frame(window)
    wFrame.pack()

def startGame():
    global wFrame, window, fGameStarted
    global paddle1, paddle2, cnv
    clearScreen()
    cnv = Canvas(wFrame, bg="#121212", width=800, height=600)
    midline = cnv.create_rectangle(395, 0, 405, 600, fill="#FFFFFF")

    roundLabel = cnv.create_text(700, 570, fill="white", text="Ronde: ", anchor="ne")
    round = cnv.create_text(710, 570, fill="white", text="0", anchor="nw")

    paddle1 = cnv.create_rectangle(10, 10, 30, 110, fill="red")
    tmpPuntenLabel1 = cnv.create_text(150, 10, fill="white", text="tmpPunten: ", anchor="ne")
    tmpPunten1 = cnv.create_text(160, 10, fill="white", text="0", anchor="nw")
    puntenLabel1 = cnv.create_text(150, 30, fill="white", text="Punten: ", anchor="ne")
    punten1 = cnv.create_text(160, 30, fill="white", text="0", anchor="nw")

    paddle2 = cnv.create_rectangle(770, 10, 790, 110, fill="blue")
    tmpPuntenLabel2 = cnv.create_text(700, 10, fill="white", text="tmpPunten: ", anchor="ne")
    tmpPunten2 = cnv.create_text(710, 10, fill="white", text="0", anchor="nw")
    puntenLabel2 = cnv.create_text(700, 30, fill="white", text="Punten: ", anchor="ne")
    punten2 = cnv.create_text(710, 30, fill="white", text="0", anchor="nw")
    # paddleBox2 = cnv.bbox(paddle2)

    ballTexture = cnv.create_rectangle(390, 290, 410, 310, fill="white")
    # ballBox = cnv.bbox(ballTexture)

    cnv.pack(fill=BOTH, expand=1)
    fGameStarted = True

    startRound()
    updateRound(cnv, round)
    updatePlayerScore(cnv, player1, punten1, tmpPunten1)
    updatePlayerScore(cnv, player2, punten2, tmpPunten2)
    updateBallPos(cnv, ballTexture)
    updatePaddlesPos(cnv, paddle1, paddle2)



if __name__ == "__main__":
    ball = Ball(395, 405, 10)

    paddleL = Paddle("L", 10, 10, 20, 100, 5, False)
    paddleR = Paddle("R", 770, 10, 20, 100, 5, False)
    player1 = Player(paddleL, 0, 0)
    player2 = Player(paddleR, 0, 0)

    round = 0


    broker = "broker.mqttdashboard.com"
    topic = "TeamCL1-4/Pong"
    client = mqtt.Client()

    fGameStarted = False

    window = Tk()
    window.title("Pi-Pong")
    window.geometry("800x600")
    wFrame = Frame(window)

    title = Label(wFrame, text="Pi-Pong!")
    title.pack()

    cnv = Canvas(wFrame, width=200, height=150)
    cnv.pack()

    btn = Button(wFrame, text="Play Game!", command=startGame)
    btn.pack()

    wFrame.pack()
    
    # window.bind("<Key>", keypress)

    try:

        client.on_connect = on_connect
        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.on_publish = on_publish

        client.connect(broker, 1883)

        client.loop_start()
        # client.loop_forever()

        window.mainloop()
        
        

    except KeyboardInterrupt:
        print("\nStopping this script.")

    except:
        print("Something went wrong.")
