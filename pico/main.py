from machine import Pin, Timer, I2C
from HCSR04 import HCSR04
from pico_i2c_lcd import I2cLcd
from round import Round
import round as round_module
import server

i2c    = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
lcd    = I2cLcd(i2c, 0x27, 2, 16)
sensor = HCSR04(trigger_pin=17, echo_pin=16)
button = Pin(2, Pin.IN, Pin.PULL_UP)
timer  = Timer()

total_rounds   = 0
current_round  = 0
scores         = [0, 0]
j1_name        = "J1"
j2_name        = "J2"


def start_game(num_rounds):
    global total_rounds, current_round, scores
    total_rounds  = num_rounds
    current_round = 0
    scores        = [0, 0]
    round_module.rounds.clear()
    server.update_game_state(game_over=False, j1_score=0, j2_score=0, state="running")
    _start_next_round()
    timer.init(mode=Timer.PERIODIC, period=60, callback=lambda t: main_loop())


def _start_next_round():
    global current_round
    current_round += 1
    Round(lcd, sensor, button, current_round)
    server.update_game_state(state="round " + str(current_round))


def stop_and_reset():
    timer.deinit()
    round_module.rounds.clear()
    global total_rounds, current_round, scores
    total_rounds  = 0
    current_round = 0
    scores        = [0, 0]
    lcd.clear()
    server.update_game_state(state="idle", game_over=False, j1_score=0, j2_score=0)


def on_game_over():
    timer.deinit()
    lcd.clear()
    lcd.putstr("J1: " + str(scores[0]) + " pts")
    lcd.move_to(0, 1)
    lcd.putstr("J2: " + str(scores[1]) + " pts")
    server.update_game_state(
        state="done",
        game_over=True,
        j1_score=scores[0],
        j2_score=scores[1]
    )


def main_loop():
    for e in round_module.rounds:
        if e.active:
            winner = e.loop()
            if winner is not None:
                if winner == 1:
                    scores[0] += 1
                elif winner == 2:
                    scores[1] += 1
                server.update_game_state(j1_score=scores[0], j2_score=scores[1])
                if current_round < total_rounds:
                    _start_next_round()
                else:
                    on_game_over()


server.set_callbacks(start_game, stop_and_reset, stop_and_reset)
server.init()

while True:
    server.poll()
