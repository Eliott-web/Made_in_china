"""
Main program for Raspberry Pi Pico
Simple LED blink example
"""

from machine import Pin, Timer
from HCSR04 import HCSR04

timer = Timer()
hcsr04 = HCSR04(trigger_pin=17, echo_pin=16)

def main_loop():

    print(hcsr04.distance_cm())

def init():
    global timer
    timer.init(mode=Timer.PERIODIC, period=60, callback=lambda t:main_loop())

init()

# Keep the program running
while True:
    pass