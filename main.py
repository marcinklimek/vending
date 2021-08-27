# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import RPi.GPIO as GPIO
import asyncio
import logging
import constans as const

logging.basicConfig(level=logging.DEBUG)


class Controller:

    def __init__(self):

        logging.debug("Start")

        self.state: int = const.STATE_IDLE
        self.flow: int = 0
        self.liquid: int = 0
        self.coins: int = 0
        self.led_time: float = 0.5
        self.timeout_timer: int = const.CANCEl_TIMEOUT

        self.setup()
        self.reset()

    def reset(self):
        self.flow = 0
        self.liquid = 0
        self.coins = 0
        self.led_time = 0.5
        self.timeout_timer = const.CANCEl_TIMEOUT

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
                self.led(True)
                await asyncio.sleep(self.led_time)

                self.led(False)
                await asyncio.sleep(self.led_time)

        except asyncio.CancelledError:
            self.led(False)

    def inc_liquid(self, amount: int):

        self.liquid += amount * 100
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

        logging.debug("coins amount = {}".format(self.coins))

    def check(self) -> bool:
        return (self.timeout_timer > 0) and (self.liquid - self.flow) > 0  # enough liquid and idle timer not timed out?

    def pump(self, state) -> None:
        GPIO.output(const.OUT_PUMP_1, state)

    def change_state(self, value):
        self.state = value

    async def run(self, loop):

        while True:

            if self.state == const.STATE_IDLE:
                if self.check():
                    self.pump(True)
                    self.change_state(const.STATE_WORKING)
                    blink = loop.create_task(self.led_task())
                    timeout = loop.create_task(self.timeout_task())

            if self.state == const.STATE_WORKING:
                if not self.check():
                    self.pump(False)
                    self.reset()
                    self.change_state(const.STATE_IDLE)

                    if blink is not None:
                        blink.cancel()

                    if timeout is not None:
                        timeout.cancel()

            await asyncio.sleep(0.1)




if __name__ == '__main__':

    ctrl = Controller()

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(ctrl.run(event_loop))

    except KeyboardInterrupt:
        pass

    finally:
        logging.debug("Closing")
        event_loop.close()
        GPIO.cleanup()
