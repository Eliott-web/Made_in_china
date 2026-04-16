from HCSR04 import HCSR04
from machine import Pin
from utime import sleep

led1 = Pin(17, Pin.OUT)
led2 = Pin(16, Pin.OUT)
sensor = HCSR04(14, 15)

def test():
    led1.on()
    led2.on()

test()

while True:
    print(sensor.distance_cm())