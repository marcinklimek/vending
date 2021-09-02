# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import RPi.GPIO as GPIO
import asyncio
import logging
import constans as const

import json
import random
import websockets

logging.basicConfig(level=logging.DEBUG)


# comminication part
async def status_server(stop_signal: asyncio.Event, message_queue: asyncio.Queue):

    clients = set()

    async def register(websocket, path):

        print("Connected")

        # Register client
        clients.add(websocket)
        try:
            # Wait forever for messages
            async for message in websocket:
                print(websocket, message)
        finally:
            try:
                clients.remove(websocket)
            except Exception:
                pass


    print("status_server before")
    async with websockets.serve(register, "127.0.0.1", 8888):

        print("status_server after serve")
        while not stop_signal.is_set():
            # TODO: there's a small bug here in that the stop signal is only checked
            #       after a message has been processed
            msg = await message_queue.get()

            print("msg: {}".format(msg))

            for client in clients:
                await client.send(msg)


class Controller:

    def __init__(self):

        logging.debug("Start")

        self.stop_signal = asyncio.Event()
        self.message_queue = asyncio.Queue()

        self.dirty = True
        self.state: int = const.STATE_IDLE
        self.flow: int = 0
        self.liquid: int = 0
        self.coins: int = 0
        self.timeout_timer: int = const.CANCEl_TIMEOUT

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
                "liquid": self.liquid }

    def setup(self) -> None:

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
        self.reset_timer()

        self.flow += 1
        self.dirty = True

        logging.debug("flow in = {}".format(self.flow))

    def button_callback(self, channel: int) -> None:
        logging.debug("button: {}".format(channel))

    def led(self, state: bool) -> None:
        GPIO.output(const.OUT_LED, state)

    def reset_timer(self):
        self.timeout_timer = const.CANCEl_TIMEOUT

    async def timeout_task(self):
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
                led_time = const.BASE_LED_TIME - (self.flow / self.liquid) * (const.BASE_LED_TIME - 0.1)

                self.led(True)
                await asyncio.sleep(led_time)

                self.led(False)
                await asyncio.sleep(led_time)

        except asyncio.CancelledError:
            self.led(False)

    def inc_liquid(self, amount: int):

        self.liquid += amount * 100
        self.dirty = True

        logging.debug("liquid = {} ({})".format(self.liquid, amount))

    def coin_callback(self, channel: int) -> None:

        self.reset_timer()

        if channel == const.IN_COIN_1:    # 1
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

        logging.debug("coins amount = {}".format(self.coins))

    def check(self) -> bool:
        return (self.timeout_timer > 0) and (self.liquid - self.flow) > 0  # enough liquid and idle timer not timed out?

    def pump(self, state) -> None:
        GPIO.output(const.OUT_PUMP_1, state)

    def change_state(self, value):
        self.state = value

    async def run(self):

        blink = None
        timeout = None

        self.ws_server_task = asyncio.create_task(
            status_server(self.stop_signal, self.message_queue) )

        while True:

            if self.state == const.STATE_IDLE:
                if self.check():
                    self.pump(True)
                    self.change_state(const.STATE_WORKING)
                    blink = asyncio.create_task(self.led_task())
                    timeout = asyncio.create_task(self.timeout_task())

            if self.state == const.STATE_WORKING:
                if not self.check():
                    self.pump(False)
                    self.reset()
                    self.change_state(const.STATE_IDLE)

                    if blink is not None:
                        blink.cancel()

                    if timeout is not None:
                        timeout.cancel()

            if self.dirty:
                self.dirty = False
                await self.message_queue.put(json.dumps(self.get_status()))

            await asyncio.sleep(0.1)

    async def stop(self):
        self.stop_signal.set()
        self.message_queue.put(json.dumps(self.get_status()))

        await self.ws_server_task


async def main():
    try:
        ctrl = Controller()
        await asyncio.create_task( ctrl.run() )

    except KeyboardInterrupt:
        pass
    finally:
        await ctrl.stop()

if __name__ == '__main__':

    try:
        asyncio.run(main())
    finally:
        logging.debug("Closing")

        GPIO.cleanup()

        # force to disable pumps
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(const.OUT_PUMP_1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(const.OUT_PUMP_2, GPIO.OUT, initial=GPIO.LOW)
