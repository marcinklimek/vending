import tkinter
import time
import math
import threading
import websockets
import asyncio
import json

class Menu:

    items = []

    def __init__(self, canvas):
        self.items.append(["Impulsy na litr", 100])
        self.items.append(["Cena za litr", 2])
        self.items_text = []
        self.canvas = canvas

    def setup_menu(self):
        self.menu_bkg = self.canvas.create_rectangle(10, 10, 1024 - 10, 600 - 10, fill='gray')


        for item in self.items:
            key_text = self.canvas.create_text(870, 10, fill="white", font="Segoe 25", anchor=tkinter.NW, text="")
            value_text = self.canvas.create_text(560, 75, fill="white", font="Segoe 25", anchor=tkinter.NW, text="")

            self.items

    def remove_menu(self):
        self.canvas.delete(self.menu_bkg)
        self.menu_bkg = None

    def draw(self, canvas):
        pass

class State:
    coins = 0
    flow = 0
    liquid = 0
    percentage = 0
    menu = False
    menu_prev = False
    menu_item_index = 0
    quit = False

state = State()


class WebSocketThread(threading.Thread):
    '''WebSocketThread will make websocket run in an a new thread'''

    # overide self init
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        print("Start thread", self.name)

    async def hello(self):
        uri = "ws://localhost:8888"

        while not state.quit:
            try:
                async with websockets.connect(uri) as websocket:
                    while not state.quit:
                        msg = await websocket.recv()
                        #print(f"<<< {msg}")

                        msg = json.loads(msg)

                        state.menu_prev = state.menu
                        state.menu = msg['menu']
                        state.menu_item_index = msg['menu_item_index']

                        state.flow = msg['flow']
                        state.liquid = msg['liquid']

                        if state.liquid == 0:
                            state.percentage = 0.0
                        else:
                            state.percentage = round( 1.0 - (state.flow / state.liquid), 2)

                        state.coins = round(msg['money'] * state.percentage, 2)

            except Exception as ex:
                print(ex)

                if state.quit:
                    return

    # overide run method
    def run(self):
        # must set a new loop for asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())
        # setup a server
        asyncio.get_event_loop().run_until_complete(self.hello())


class UI:

    def __init__(self):

        self.root = tkinter.Tk()
        self.root.geometry('1024x600')
        self.root.resizable(0, 0)
        self.root.resizable(False, False)
        self.root.resizable(width=False, height=False)

        self.canvas = tkinter.Canvas(
            self.root,
            width=1024,
            height=600
        )
        self.canvas.pack()

        self.img = tkinter.PhotoImage(file='bin/bkg.png')
        self.canvas.create_image(
            0,
            0,
            anchor=tkinter.NW,
            image=self.img
        )

        self.time_current = ''

        self.setup_texts()

        self.menu_bkg = None

        self.time_text = self.canvas.create_text(870, 10, fill="white", font="Segoe 25", anchor=tkinter.NW, text="")
        self.title_text = self.canvas.create_text(560,  75, fill="white", font="Segoe 25", anchor=tkinter.NW, text="")
        self.price_text = self.canvas.create_text(306, 545, fill="white", font="Segoe 20", anchor=tkinter.NW, text="")
        self.start_text = self.canvas.create_text(856, 560, fill="white", font="Segoe 25", anchor=tkinter.NW, text="")
        self.company_text = self.canvas.create_text(10, 10, fill="white", font="Segoe 25", anchor=tkinter.NW, text="")

        self.coins_text = self.canvas.create_text(750, 240, fill="#56f7f5", font="Segoe 60 bold", anchor=tkinter.CENTER, text="")
        self.coins_currency_text = self.canvas.create_text(750, 370, fill="#56f7f5", font="Segoe 25", anchor=tkinter.CENTER,
                                                  text="")

        self.liquid_perc_text = self.canvas.create_text(470, 240, fill="#56f7f5", font="Segoe 25 bold", anchor=tkinter.CENTER,
                                                  text="")

        self.update_texts()

    def setup_menu(self):
        self.canvas.itemconfig(self.coins_text, text="")
        self.canvas.itemconfig(self.liquid_perc_text, text="")

        self.menu_bkg = self.canvas.create_rectangle(10, 10, 1024 - 10, 600 - 10, fill='gray')

    def remove_menu(self):
        self.canvas.delete(self.menu_bkg)
        self.menu_bkg = None

    def setup_texts(self):
        self.title_str = "Dystrybutor płynu"
        self.price_str = "Cena jednego litra płynu: {} PLN"
        self.start_str = "START"
        self.company_str = "FIRMA ABC"
        self.coins_currency_str = "PLN"

        self.price_value = 2
        self.coins = 0
        self.flow = 0
        self.liquid = 0

    def update_coins_flow(self):

        #add rect with menu bkg
        if state.menu and not state.menu_prev:
            self.setup_menu()
            state.menu_prev = state.menu

        if not state.menu and state.menu_prev:
            self.remove_menu()
            state.menu_prev = state.menu

        if state.menu:
            pass
        else:
            self.canvas.itemconfig(self.coins_text, text=state.coins)
            self.canvas.itemconfig(self.liquid_perc_text, text=state.percentage)


    def update_texts(self):
        self.canvas.itemconfig(self.title_text, text=self.title_str)
        self.canvas.itemconfig(self.price_text, text=self.price_str.format(self.price_value))
        self.canvas.itemconfig(self.start_text, text=self.start_str)
        self.canvas.itemconfig(self.company_text, text=self.company_str)
        self.canvas.itemconfig(self.coins_text, text=self.coins_currency_str)
        self.canvas.itemconfig(self.coins_currency_text, text=self.coins_currency_str)

    def tick(self):
        time_str = time.strftime('%H:%M:%S')

        if time_str != self.time_current:
            self.time_current = time_str

            self.canvas.itemconfig(self.time_text, text=self.time_current)

        self.root.after(200, self.tick)

    def update(self):
        self.update_coins_flow()
        self.root.after(100, self.update)

    def run(self):
        self.tick()
        self.update()

        self.root.mainloop()


"""class Circle(tkinter.Shape):
    def __init__(self, canvas, x, y, radius):
        super(Circle, self).__init__(canvas, x, y)
        self.radius = radius

    def draw(self):
        left = self.x - self.radius * math.sqrt(2)
        right = self.x + self.radius * math.sqrt(2)
        top = self.y - self.radius * math.sqrt(2)
        bottom = self.y + self.radius * math.sqrt(2)
        self.canvas.create_oval(left, top, right, bottom)


class Rectangle(tkinter.Shape):
    def __init__(self, canvas, x, y, right, bottom):
        super(Rectangle, self).__init__(canvas, x, y)
        self.right = right
        self.bottom = bottom

    def draw(self):
        left = 2 * self.x - self.right
        right = self.right
        top = 2 * self.y - self.bottom
        bottom = self.bottom
        self.canvas.create_rectangle(left, top, right, bottom)"""

if __name__ == '__main__':

    threadWebSocket = WebSocketThread("client")
    threadWebSocket.start()

    try:
        UI().run()
    except Exception:
        print("Quit")
    finally:
        print("Cleaning")
        state.quit = True
        threadWebSocket.join()

