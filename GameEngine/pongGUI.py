import tkinter as tk

window = tk.Tk()

title = tk.Label(window, text="Pi-Pong!")
title.pack()

cnv = tk.Canvas(window, width=200, height=150)
cnv.pack()

btn = tk.Button(window, text="Play Game!")
btn.pack()

window.mainloop()