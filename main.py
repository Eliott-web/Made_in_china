"""
Main program for Raspberry Pi Pico
Simple LED blink example
"""

from machine import Pin, Timer
import time
timer = Timer()
trig = Pin(17, Pin.OUT)
echo = Pin(16, Pin.IN, Pin.PULL_DOWN)

def main_loop():
    trig.value(0)
    time.sleep(0.1)
    trig.value(1)
    time.sleep_us(2)
    trig.value(0)
    while echo.value()==0:
        pulse_start = time.ticks_us()
    while echo.value()==1:
        pulse_end = time.ticks_us()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17165 / 1000000
    distance = round(distance, 0)
    print ('Distance:',"{:.0f}".format(distance),'cm')

def init():
    global timer
    timer.init(mode=Timer.PERIODIC, period=60, callback=lambda t:main_loop())

init()

# Keep the program running
while True:
    pass