# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import RPi.GPIO as GPIO
import asyncio
import logging
import constans as const

logging.basicConfig(level=logging.DEBUG)


class Controller:

    def __init__(self):
        self.flow: int = 0
        self.liquid: int = 0
        self.coins: int = 0
        self.led_time: float = 0.5

        self.coins_queue = asyncio.Queue()

        self.setup()

        self.reset()

    def reset(self):
        self.flow = 0
        self.liquid = 0
        self.coins = 0

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

        self.flow += 1
        logging.debug("flow in = {}".format(self.flow))

    def button_callback(self, channel: int) -> None:
        logging.debug("button: {}".format(channel))

    def led(self, state: bool) -> None:
        GPIO.output(const.OUT_LED, state)

    async def led_task(self):
        try:
            while True:
                self.led(True)
                await asyncio.sleep(self.led_time)

                self.led(False)
                await asyncio.sleep(self.led_time)

        except asyncio.CancelledError:
            self.led(False)

    def coin_callback(self, channel: int) -> None:
        logging.debug("coins: {}".format(channel))

        if channel == const.IN_COIN_1:  # 1
            self.coins = self.coins + 1
        elif channel == const.IN_COIN_2:  # 2
            self.coins = self.coins + 2
        elif channel == const.IN_COIN_3:  # 5
            self.coins = self.coins + 5

        logging.debug("coins = {}".format(self.coins))

    def run(self):

        while True:

            if self.coins > 0:
                pass
                # start pump
            else:
                pass
                # stop pump


if __name__ == '__main__':

    ctrl = Controller()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(ctrl.run())

    except KeyboardInterrupt:
        pass

    finally:
        print("[debug] Closing")
        loop.close()
        GPIO.cleanup()
