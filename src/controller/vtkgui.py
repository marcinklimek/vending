import tkinter
import time

root = tkinter.Tk()
root.geometry('1024x600')
root.resizable(0, 0)
root.resizable(False, False)
root.resizable(width=False, height=False)
#root.wm_attributes('-transparentcolor','black')

canvas = tkinter.Canvas(
    root,
    width=1024,
    height=600
)
canvas.pack()

img = tkinter.PhotoImage(file='bin/bkg.png')
canvas.create_image(
    0,
    0,
    anchor=tkinter.NW,
    image=img
)

time1 = ''

title_text = canvas.create_text(560,  75, fill="white", font="Segoe 25 bold", anchor=tkinter.NW, text="Dystrybutor płynu")
price_text = canvas.create_text(306, 545, fill="white", font="Segoe 25 bold", anchor=tkinter.NW, text="Cena jednego litra płynu: 2 PLN")
start_text = canvas.create_text(856, 570, fill="white", font="Segoe 25 bold", anchor=tkinter.NW, text="START")
company_text = canvas.create_text(10, 10, fill="white", font="Segoe 25 bold", anchor=tkinter.NW, text="FIRMA ABC")

def tick():
    global time1

    time2 = time.strftime('%H:%M:%S')

    if time2 != time1:
        time1 = time2

        #canvas.itemconfig(mytext, text=time2)

    root.after(200, tick)


tick()
root.mainloop()
