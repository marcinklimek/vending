# https://pythonguides.com/python-tkinter-image/

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import platform

useGpio = True  # on rpi

if platform.system() == "Windows":
    useGpio = False
    import keyboard
else:
    import RPi.GPIO as GPIO

import asyncio
import logging
import constans as const

import json
import random
import websockets
from syncer import sync

from threading import RLock
lock = RLock()

global_dict = {}

logging.basicConfig(level=logging.INFO)


# comminication part
async def status_server(stop_signal: asyncio.Event, message_queue: asyncio.Queue, ctrl):
    clients = set()

    async def register(websocket, path):

        print("Connected")

        # Register client
        clients.add(websocket)
        ctrl.dirty = True
        try:
            # Wait forever for messages
            async for message in websocket:
                print(websocket, message)
        except Exception:
            pass
        finally:
            try:
                clients.remove(websocket)
            except Exception:
                pass


    async with websockets.serve(register, "127.0.0.1", 8888):

        print("status_server after serve")
        while not stop_signal.is_set():

            msg = await message_queue.get()

            print("msg: {}".format(msg))

            for client in clients:
                await client.send(msg)


class Controller:

    def __init__(self):

        logging.debug("Start")

        self.stop_signal = asyncio.Event()
        self.message_queue = asyncio.Queue()

        self.menuOn = False
        self.prev_menu = True

        self.menu_item_index = 0
        self.menu_item_max = 1
        self.menu_values = [100, 2]

        self.dirty = True
        self.state: int = const.STATE_IDLE
        self.flow: int = 0
        self.liquid: int = 0
        self.coins: int = 0
        self.timeout_timer: int = const.CANCEl_TIMEOUT

        self.ws_server_task = None

        self.setup()
        self.reset()

    def reset(self):

        self.flow = 0
        self.liquid = 0
        self.coins = 0
        self.timeout_timer = const.CANCEl_TIMEOUT
        self.dirty = True

    def get_status(self):
        return {"money": self.coins,
                "liquid": self.liquid,
                "flow": self.flow,
                "menu": self.menuOn,
                "menu_item_index": self.menu_item_index,
                "menu_values": self.menu_values}

    def print_pressed_keys(self, e):
        scan_code = e.scan_code

        """
        print(scan_code)
        """

        if scan_code == 33:   # letter f - flow
            self.flow_sensor_callback(1)
        else:
            if e.event_type == "up":
                if scan_code == 2:   # 1
                    self.coin_callback(const.IN_COIN_1)
                elif scan_code == 3:   # 2
                    self.coin_callback(const.IN_COIN_2)
                elif scan_code == 6:   # 5
                    self.coin_callback(const.IN_COIN_3)
                elif scan_code == 31:  # letter s
                    pass
                elif scan_code == 72:  # up (enter menu/ exit menu)
                    self.process_menu(const.IN_UP)
                elif scan_code == 80:  # down (next item)
                    self.process_menu(const.IN_DOWN)
                elif scan_code == 77:  # right (inc)
                    self.process_menu(const.IN_RIGHT)
                elif scan_code == 75:  # left  (dec)
                    self.process_menu(const.IN_LEFT)
                #elif scan_code == 1:   # esc
                #    self.stop()

    def process_menu(self, key):
        if key == const.IN_UP:
            self.menuOn = not self.menuOn

        if self.menuOn:
            if key == const.IN_DOWN:
                self.menu_item_index = self.menu_item_index + 1
                if self.menu_item_index > self.menu_item_max:
                    self.menu_item_index = 0

            elif key == const.IN_RIGHT:
                v = self.menu_values[self.menu_item_index] + 1
                if v > 1000:
                    v = 1000
                self.menu_values[self.menu_item_index] = v

            elif key == const.IN_LEFT:
                v = self.menu_values[self.menu_item_index] - 1
                if v < 0:
                    v = 0
                self.menu_values[self.menu_item_index] = v

        self.dirty = True


    def setup(self) -> None:

        if not useGpio:
            keyboard.hook(self.print_pressed_keys)
            return

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(True)

        GPIO.setup(const.OUT_LED, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(const.OUT_PUMP_1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(const.OUT_PUMP_2, GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(const.IN_FLOW_SENSOR, GPIO.IN)

        GPIO.setup(const.IN_ENTER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(const.IN_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(const.IN_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(const.IN_CANCEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(const.IN_START, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(const.IN_CANCEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(const.IN_COIN_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(const.IN_COIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(const.IN_COIN_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(const.IN_COIN_TERMINAL, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # events
        GPIO.add_event_detect(const.IN_FLOW_SENSOR, GPIO.RISING, callback=self.flow_sensor_callback)

        GPIO.add_event_detect(const.IN_ENTER, GPIO.FALLING, callback=self.button_callback)
        GPIO.add_event_detect(const.IN_UP, GPIO.FALLING, callback=self.button_callback)
        GPIO.add_event_detect(const.IN_DOWN, GPIO.FALLING, callback=self.button_callback)
        GPIO.add_event_detect(const.IN_CANCEL, GPIO.FALLING, callback=self.button_callback)

        GPIO.add_event_detect(const.IN_COIN_1, GPIO.RISING, callback=self.coin_callback)
        GPIO.add_event_detect(const.IN_COIN_2, GPIO.RISING, callback=self.coin_callback)
        GPIO.add_event_detect(const.IN_COIN_3, GPIO.RISING, callback=self.coin_callback)
        GPIO.add_event_detect(const.IN_COIN_TERMINAL, GPIO.RISING, callback=self.coin_callback)

    def flow_sensor_callback(self, channel: int) -> None:

        if self.liquid > 0:
            self.flow += 1
            self.dirty = True

            logging.debug("flow in = {}".format(self.flow))

    def button_callback(self, channel: int) -> None:
        logging.debug("button: {}".format(channel))

    def led(self, state: bool) -> None:
        if not useGpio:
            logging.debug("led: {}".format(state))
            return

        GPIO.output(const.OUT_LED, state)

    def reset_timer(self):
        self.timeout_timer = const.CANCEl_TIMEOUT

    async def timeout_task(self):
        logging.debug("timeout_task start")
        try:
            while True:
                await asyncio.sleep(1)

                if self.timeout_timer > 0:
                    self.timeout_timer -= 1
                    logging.info("timeout timer: {}".format(self.timeout_timer))

        except asyncio.CancelledError:
            self.reset_timer()

    async def led_task(self):
        try:
            while True:
                if self.liquid > 0 and self.flow > 0:
                    led_time = const.BASE_LED_TIME - (self.flow / self.liquid) * (const.BASE_LED_TIME - 0.1)
                else:
                    led_time = const.BASE_LED_TIME

                self.led(True)
                await asyncio.sleep(led_time)

                self.led(False)
                await asyncio.sleep(led_time)

        except asyncio.CancelledError:
            self.led(False)

    def inc_liquid(self, amount: int):

        self.liquid += round((amount / self.menu_values[const.LITER_PRICE]) * self.menu_values[const.TICK_PER_LITER])
        self.dirty = True

        logging.debug("liquid = {} ({})".format(self.liquid, amount))

    def coin_callback(self, channel: int) -> None:

        if channel == const.IN_COIN_1:  # 1
            self.coins = self.coins + 1
            self.inc_liquid(1)
        elif channel == const.IN_COIN_2:  # 2
            self.coins = self.coins + 2
            self.inc_liquid(2)
        elif channel == const.IN_COIN_3:  # 5
            self.coins = self.coins + 5
            self.inc_liquid(5)
        elif channel == const.IN_COIN_TERMINAL:
            self.coins = self.coins + 1
            self.inc_liquid(1)

        self.dirty = True


    def check(self) -> bool:
        return (self.timeout_timer > 0) and (self.liquid - self.flow) > 0  # enough liquid and idle timer not timed out?

    def pump(self, state) -> None:
        if not useGpio:
            logging.debug("pump = {}".format(state))
            return

        GPIO.output(const.OUT_PUMP_1, state)

    def change_state(self, value):
        self.state = value
        self.dirty = True

    async def run(self, loop):

        self.loop = loop
        blink = None
        timeout = None

        self.ws_server_task = loop.create_task(
            status_server(self.stop_signal, self.message_queue, self))

        while True:

            if self.state == const.STATE_MENU:
                logging.debug(f"state: STATE_MENU m:{self.menuOn}")

                if self.timeout_timer == 0:
                    self.menuOn = False

                if not self.menuOn:
                    self.change_state(const.STATE_IDLE)

                    if timeout is not None:
                        timeout.cancel()
                        timeout = None

            elif self.state == const.STATE_IDLE:

                logging.debug(f"state: STATE_IDLE  m:{self.menuOn}")

                if self.menuOn:
                    self.change_state(const.STATE_MENU)
                    if timeout is None:
                        timeout = loop.create_task(self.timeout_task())

                elif self.check():
                    self.pump(True)
                    self.change_state(const.STATE_WORKING)
                    blink = loop.create_task(self.led_task())
                    if timeout is None:
                        timeout = loop.create_task(self.timeout_task())

            elif self.state == const.STATE_WORKING:

                logging.debug(f"state: STATE_WORKING")

                if self.menuOn:
                    self.change_state(const.STATE_MENU)

                elif not self.check():
                    self.pump(False)
                    self.reset()
                    self.change_state(const.STATE_IDLE)

                    if blink is not None:
                        blink.cancel()

                    if timeout is not None:
                        timeout.cancel()
                        timeout = None

            if self.dirty:
                self.dirty = False
                self.reset_timer()
                await self.message_queue.put(json.dumps(self.get_status()))

            await asyncio.sleep(0.1)

    def stop(self):

        self.stop_signal.set()
        self.loop.stop()


def main():
    try:
        ctrl = Controller()
        loop = asyncio.get_event_loop()
        loop.create_task(ctrl.run(loop))
        loop.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        ctrl.stop()

        if useGpio:
            GPIO.cleanup()

            # force to disable pumps
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(const.OUT_PUMP_1, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(const.OUT_PUMP_2, GPIO.OUT, initial=GPIO.LOW)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        logging.debug("Closing")


