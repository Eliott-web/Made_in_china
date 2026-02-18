"""
Main program for Raspberry Pi Pico
Simple LED blink example
"""
from component.HCSR04 import HCSR04
from machine import Pin
from utime import sleep

def testMesure():
    sensor = HCSR04(trigger_pin=17, echo_pin=16)
    while True:
        print('Distance: {} mm'.format(sensor.distance_mm()))
        sleep(1)

def main():
    testMesure()
    led = Pin(0, Pin.OUT)

    #while True:
        #led.toggle()
        #sleep(1)  # Blink every second

if __name__ == "__main__":
    main()
