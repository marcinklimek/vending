# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import RPi.GPIO as GPIO
import asyncio

GPIO06 = 31
GPIO07 = 26
GPIO08 = 24
GPIO12 = 32
GPIO13 = 33
GPIO14 = 8
GPIO15 = 10
GPIO16 = 36
GPIO18 = 12
GPIO18 = 12
GPIO19 = 35
GPIO20 = 38
GPIO23 = 16
GPIO23 = 16
GPIO24 = 18
GPIO25 = 22
GPIO26 = 37

OUT_LED = GPIO20
OUT_PUMP_1 = GPIO16
OUT_PUMP_2 = GPIO12
IN_FLOW_SENSOR = GPIO07

IN_ENTER = GPIO06
IN_DOWN = GPIO13
IN_UP = GPIO19
IN_CANCEL = GPIO26

IN_START = GPIO24
IN_STOP = GPIO25


def flow_sensor_callback(channel):
    print("[debug] flow in")


def buttons_callback(channel):
    print("[debug] buttons: {}".format(channel))


def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(True)

    GPIO.setup(OUT_LED, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(OUT_PUMP_1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(OUT_PUMP_2, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(IN_FLOW_SENSOR, GPIO.IN)

    GPIO.setup(IN_ENTER, GPIO.IN)
    GPIO.setup(IN_UP, GPIO.IN)
    GPIO.setup(IN_DOWN, GPIO.IN)
    GPIO.setup(IN_CANCEL, GPIO.IN)

    # events
    GPIO.add_event_detect(IN_FLOW_SENSOR, GPIO.RISING, callback=flow_sensor_callback)

    GPIO.add_event_detect(IN_ENTER, GPIO.FALLING, callback=buttons_callback)
    GPIO.add_event_detect(IN_UP, GPIO.FALLING, callback=buttons_callback)
    GPIO.add_event_detect(IN_DOWN, GPIO.FALLING, callback=buttons_callback)
    GPIO.add_event_detect(IN_CANCEL, GPIO.FALLING, callback=buttons_callback)


async def worker():
    while True:
        await asyncio.sleep(1)
        print("First Worker Executed")

if __name__ == '__main__':

    setup()

    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(worker())
        loop.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        print("[debug] Closing")
        loop.close()
        GPIO.cleanup()