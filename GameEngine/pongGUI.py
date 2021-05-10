from tkinter import *

fGameStarted = False

def updateBallPos(canvas, ball):
    canvas.move(ball, 5, 5)
    canvas.after(100, updateBallPos, canvas, ball)

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

    paddle1 = cnv.create_rectangle(10, 10, 30, 100, fill="red")
    paddleBox1 = cnv.bbox(paddle1)

    paddle2 = cnv.create_rectangle(770, 10, 790, 100, fill="blue")
    paddleBox2 = cnv.bbox(paddle2)

    ball = cnv.create_rectangle(390, 290, 410, 310, fill="white")
    ballBox = cnv.bbox(ball)

    cnv.pack(fill=BOTH, expand=1)
    fGameStarted = True
    updateBallPos(cnv, ball)


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

def keypress(event):
    y1 = 0
    if event.char == "w": y1 = -10
    elif event.char == "s": y1 = 10
    cnv.move(paddle1, 0, y1)
    
    y2 = 0
    if event.char == "o": y2 = -10
    elif event.char == "l": y2 = 10
    cnv.move(paddle2, 0, y2)



 
window.bind("<Key>", keypress)

window.mainloop()