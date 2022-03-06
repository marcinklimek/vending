# -*- coding: utf-8 -*-

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
import websockets

from os.path import exists

logging.basicConfig(level=logging.INFO)


def save_json(file_name, file_content):
    with open(file_name, 'w', encoding='utf-8') as fj:
        json.dump(file_content, fj, ensure_ascii=False, indent=4)


def load_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as fj:
        return json.load(fj)


# comminication part
async def status_server(stop_signal: asyncio.Event, message_queue: asyncio.Queue, ctrl):
    clients = set()

    async def register(websocket, path):

        logging.debug("Connected")

        # Register client
        clients.add(websocket)
        ctrl.dirty = True
        try:
            # Wait forever for messages
            async for message in websocket:
                logging.debug(websocket, message)
        except Exception as ex:
            logging.error(f"Exception in server/register {str(ex)}")
        finally:
            try:
                clients.remove(websocket)
            except Exception as ex:
                logging.error(f"Exception in server/client remove {str(ex)}")

    async with websockets.serve(register, "127.0.0.1", 8888):

        logging.debug("status_server after serve")
        while not stop_signal.is_set():

            msg = await message_queue.get()

            logging.debug("msg: {}".format(msg))

            for client in clients:
                await client.send(msg)


class Controller:

    def __init__(self):

        logging.info("Start")

        self.loop = None

        self.pump_state = False

        self.stop_signal = asyncio.Event()
        self.message_queue = asyncio.Queue()

        self.menuOn = False
        self.prev_menu = True

        self.menu_item_index = 0
        
        self.menu_item_max = len(const.menu_types) - 1

        if exists("config.json"):
            self.menu_values = load_json("config.json")
            if len(self.menu_values) == 2:
                self.menu_values.append(0)
                self.menu_values.append(None)
        else:
            self.menu_values = [100, 2, 0, None]
            save_json("config.json", self.menu_values)

        if exists("stats.json"):
            self.money_stats = load_json("stats.json")
        else:
            self.money_stats = [0, 0]
            save_json("stats.json", self.money_stats)

        if exists("flow.json"):
            self.flow_stats = load_json("flow.json")
        else:
            self.flow_stats = 0
            save_json("flow.json", self.flow_stats)

        self.dirty = True
        self.state: int = const.STATE_IDLE
        self.flow: int = 0

        self.liquid: int = 0
        self.money: int = 0

        self.timeout_timer: int = const.CANCEl_TIMEOUT

        self.ws_server_task = None

        self.setup()
        self.reset()

    def reset(self):

        self.flow = 0
        self.liquid = 0
        self.money = 0
        self.timeout_timer = const.CANCEl_TIMEOUT
        self.dirty = True

    def reset_local_stats(self):
        self.money_stats[const.MONEY_STATS_CURRENT] = 0
        self.save()

    def get_status(self):
        return {"money": round(self.money, 2),
                "liquid": self.liquid,
                "flow": self.flow,
                "menu": self.menuOn,
                "menu_item_index": self.menu_item_index,
                "menu_values": self.menu_values,
                "money_stats": self.money_stats,
                "flow_stats": round(self.flow_stats / self.menu_values[const.TICK_PER_LITER], 2),
                }

    def save(self):
        save_json("stats.json", self.money_stats)
        save_json("flow.json", self.flow_stats)

    def print_pressed_keys(self, e):
        scan_code = e.scan_code

        """
        logging.debug(scan_code)
        """

        if scan_code == 33:  # letter f - flow
            self.flow_sensor_callback(1)
        else:
            if e.event_type == "up":
                if scan_code == 2:  # 1
                    self.coin_callback(const.IN_COIN_1)
                elif scan_code == 3:  # 2
                    self.coin_callback(const.IN_COIN_2)
                elif scan_code == 6:  # 5
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
                # elif scan_code == 1:   # esc
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

                if const.menu_types[self.menu_item_index] == const.MENU_TYPE_RESET:
                    self.reset_local_stats()
                else:
                    if const.menu_types[self.menu_item_index] == const.MENU_TYPE_FLOAT:
                        v = round(self.menu_values[self.menu_item_index] + 0.01, 2)

                    if const.menu_types[self.menu_item_index] == const.MENU_TYPE_INT:
                        v = self.menu_values[self.menu_item_index] + 1

                    if const.menu_types[self.menu_item_index] == const.MENU_TYPE_LIST:
                        v = self.menu_values[self.menu_item_index] + 1

                        max_idx = len(const.menu_items_list[self.menu_item_index]) - 1
                        if v > max_idx:
                           v = max_idx

                    if v > 1000:
                        v = 1000

                    self.menu_values[self.menu_item_index] = v

                    save_json("config.json", self.menu_values)

            elif key == const.IN_LEFT:

                if const.menu_types[self.menu_item_index] == const.MENU_TYPE_RESET:
                    self.reset_local_stats()
                    v = None
                else:
                    if const.menu_types[self.menu_item_index] == const.MENU_TYPE_FLOAT:
                        v = round(self.menu_values[self.menu_item_index] - 0.01, 2)

                    if const.menu_types[self.menu_item_index] == const.MENU_TYPE_INT:
                        v = self.menu_values[self.menu_item_index] - 1

                    if const.menu_types[self.menu_item_index] == const.MENU_TYPE_LIST:
                        v = self.menu_values[self.menu_item_index] - 1

                    if v < 0:
                        v = 0

                    self.menu_values[self.menu_item_index] = v

                    save_json("config.json", self.menu_values)

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
        GPIO.add_event_detect(const.IN_FLOW_SENSOR, GPIO.RISING, callback=self.flow_sensor_callback, bouncetime=50)

        GPIO.add_event_detect(const.IN_ENTER, GPIO.FALLING, callback=self.button_callback, bouncetime=200)
        GPIO.add_event_detect(const.IN_UP, GPIO.FALLING, callback=self.button_callback, bouncetime=200)
        GPIO.add_event_detect(const.IN_DOWN, GPIO.FALLING, callback=self.button_callback, bouncetime=200)
        GPIO.add_event_detect(const.IN_CANCEL, GPIO.FALLING, callback=self.button_callback, bouncetime=200)

        GPIO.add_event_detect(const.IN_COIN_1, GPIO.RISING, callback=self.coin_callback, bouncetime=300)
        GPIO.add_event_detect(const.IN_COIN_2, GPIO.RISING, callback=self.coin_callback, bouncetime=300)
        GPIO.add_event_detect(const.IN_COIN_3, GPIO.RISING, callback=self.coin_callback, bouncetime=300)
        GPIO.add_event_detect(const.IN_COIN_TERMINAL, GPIO.RISING, callback=self.coin_callback, bouncetime=300)

    def flow_sensor_callback(self, channel: int) -> None:

        if self.liquid > 0 and self.pump_state:
            self.flow_stats += 1
            self.flow += 1
            self.dirty = True

            self.money = self.money - self.menu_values[const.LITER_PRICE]/self.menu_values[const.TICK_PER_LITER]

            self.save()

            logging.debug("flow in = {}".format(self.flow))

    def button_callback(self, channel: int) -> None:
        logging.debug("button: {}".format(channel))

        if channel == const.IN_UP:  # up (enter menu/ exit menu)
            self.process_menu(const.IN_UP)
        elif channel == const.IN_DOWN:  # down (next item)
            self.process_menu(const.IN_DOWN)
        elif channel == const.IN_ENTER:  # right (inc)
            self.process_menu(const.IN_RIGHT)
        elif channel == const.IN_CANCEL:  # left  (dec)
            self.process_menu(const.IN_LEFT)

    def led(self, state: bool) -> None:
        if not useGpio:
            logging.debug("led: {}".format(state))
            return

        GPIO.output(const.OUT_LED, state)

    def reset_timer(self):
        self.timeout_timer = const.CANCEl_TIMEOUT

    # rozbieg pompy, zanim zaczynamy liczyc impulsy
    async def pump_starting_timeout_task(self):

        await asyncio.sleep(2)
        self.pump_state = True
        logging.info("pump = True (delayed)")

    async def timeout_task(self):
        logging.debug("timeout_task start")
        try:
            while True:
                await asyncio.sleep(1)

                if self.timeout_timer > 0:
                    self.timeout_timer -= 1
                    logging.debug("timeout timer: {}".format(self.timeout_timer))

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

        self.liquid += round((amount / self.menu_values[const.LITER_PRICE]) * self.menu_values[const.TICK_PER_LITER], 2)
        self.dirty = True

        logging.info("liquid = {} ({})".format(self.liquid, amount))

    def coin_callback(self, channel: int) -> None:

        if channel == const.IN_COIN_1:  # 1

            self.money_stats[const.MONEY_STATS_GLOBAL] += 1
            self.money_stats[const.MONEY_STATS_CURRENT] += 1

            self.money = self.money + 1
            self.inc_liquid(1)

        elif channel == const.IN_COIN_2:  # 2

            self.money_stats[const.MONEY_STATS_GLOBAL] += 2
            self.money_stats[const.MONEY_STATS_CURRENT] += 2

            self.money = self.money + 2
            self.inc_liquid(2)

        elif channel == const.IN_COIN_3:  # 5

            self.money_stats[const.MONEY_STATS_GLOBAL] += 5
            self.money_stats[const.MONEY_STATS_CURRENT] += 5

            self.money = self.money + 5
            self.inc_liquid(5)

        elif channel == const.IN_COIN_TERMINAL:

            self.money_stats[const.MONEY_STATS_GLOBAL] += 1
            self.money_stats[const.MONEY_STATS_LOCAL] += 1

            self.money = self.money + 1
            self.inc_liquid(1)

        self.save()
        self.dirty = True

    def check(self) -> bool:
        return (self.timeout_timer > 0) and (self.liquid - self.flow) > 0  # enough liquid and idle timer not timed out?

    def pump(self, state) -> None:
        if not useGpio:
            if self.pump_state is False and state is True:
                self.loop.create_task(self.pump_starting_timeout_task())
            else:
                logging.info(f"pump = {state}")
                self.pump_state = state

            return

        if self.pump_state is False and state is True:
            GPIO.output(const.OUT_PUMP_1, True)
            GPIO.output(const.OUT_PUMP_2, True)
            self.loop.create_task(self.pump_starting_timeout_task())
        else:
            logging.info(f"pump = {state}")
            self.pump_state = state
            GPIO.output(const.OUT_PUMP_1, state)
            GPIO.output(const.OUT_PUMP_2, state)

    def change_state(self, value):

        logging.info(f"change state from: {const.state_str[self.state]} to {const.state_str[value]}")

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

                if self.timeout_timer == 0:
                    self.menuOn = False

                if not self.menuOn:
                    self.change_state(const.STATE_IDLE)

                    if timeout is not None:
                        timeout.cancel()
                        timeout = None

            elif self.state == const.STATE_IDLE:

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
        logging.info("Closing")
