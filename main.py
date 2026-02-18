"""
Main program for Raspberry Pi Pico
Simple LED blink example
"""
#from component.HCSR04 import HCSR04
# from machine import Pin
# from time import sleep

# def testMesure():
#     sensor = HCSR04(trigger_pin=17, echo_pin=16)
#     while True:
#         print('Distance: {} mm'.format(sensor.distance_mm()))
#         print(sensor.distance_mm())
#         sleep(1)

# def main():
#     testMesure()
#     led = Pin(0, Pin.OUT)

#     #while True:
#         #led.toggle()
#         #sleep(1)  # Blink every second

# if __name__ == "__main__":
#     main()

from machine import Pin
import time
trig = Pin(17, Pin.OUT)
echo = Pin(16, Pin.IN, Pin.PULL_DOWN)
while True:
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
    time.sleep(1)