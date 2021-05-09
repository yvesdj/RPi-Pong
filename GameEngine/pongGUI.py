from tkinter import *

def startGame():
    global wFrame, window
    wFrame.destroy()
    wFrame = Frame(window)
    wFrame.pack()

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

window.mainloop()