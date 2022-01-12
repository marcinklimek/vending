import tkinter
import time

root = tkinter.Tk()
time1 = ''
clock = tkinter.Label(root, font=('times', 20, 'bold'), bg='green')
clock.pack(fill=tkinter.BOTH, expand=1)

def tick():
    global time1

    time2 = time.strftime('%H:%M:%S')

    if time2 != time1:
        time1 = time2
        clock.config(text=time2)

    root.after(200, tick)

tick()
root.mainloop()