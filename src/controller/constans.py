GPIO06 = 31
GPIO07 = 26
GPIO08 = 24
GPIO12 = 32
GPIO13 = 33
GPIO14 = 8
GPIO15 = 10
GPIO16 = 36
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

IN_RIGHT = IN_ENTER
IN_LEFT = IN_CANCEL

IN_START = GPIO24
IN_STOP = GPIO25

IN_COIN_1 = GPIO15
IN_COIN_2 = GPIO18
IN_COIN_3 = GPIO14
IN_COIN_TERMINAL = GPIO23


STATE_IDLE = 0
STATE_WORKING = 1
STATE_MENU = 2

state_str = {STATE_IDLE:"IDLE", STATE_WORKING:"WORKING", STATE_MENU:"MENU"}

BASE_LED_TIME = 0.5

CANCEl_TIMEOUT = 60*2

TICK_PER_LITER = 0
LITER_PRICE = 1

MENU_TYPE_INT = 0
MENU_TYPE_FLOAT = 1
MENU_TYPE_RESET = 2
MENU_TYPE_LIST = 3


menu_items = ("Impulsy na litr", "Cena za litr", "Rodzaj", "Reset licznika")
menu_types = [MENU_TYPE_INT, MENU_TYPE_FLOAT, MENU_TYPE_LIST, MENU_TYPE_RESET]
menu_items_list = ((), (), ("letni", "zimowy"), ())
screen_items_list = ((), (), ("letniego", "zimowego"), ())

MONEY_STATS_CURRENT = 0
MONEY_STATS_GLOBAL  = 1