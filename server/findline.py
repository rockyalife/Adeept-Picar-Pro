#!/usr/bin/python3
# File name   : findline.py
# Description : line tracking 
# Website     : www.gewbot.com
# Author      : William
# Date        : 2019/08/28
import time
import move
from gpiozero import DigitalInputDevice
'''
status     = 1          #Motor rotation
forward    = 1          #Motor forward
backward   = 0          #Motor backward

left_spd   = num_import_int('E_M1:')         #Speed of the car
right_spd  = num_import_int('E_M2:')         #Speed of the car
left       = num_import_int('E_T1:')         #Motor Left
right      = num_import_int('E_T2:')         #Motor Right
'''
# Define GPIO pins for line tracking sensors
line_pin_right = DigitalInputDevice(19, pull_up=False)
line_pin_middle = DigitalInputDevice(16, pull_up=False)
line_pin_left = DigitalInputDevice(20, pull_up=False)
'''
left_R = 15
left_G = 16
left_B = 18

right_R = 19
right_G = 21
right_B = 22

on  = GPIO.LOW
off = GPIO.HIGH

spd_ad_1 = 1
spd_ad_2 = 1
'''

def run():
    """
    Reads the line sensor values and controls motor movement accordingly.
    """
    status_right = line_pin_right.value
    status_middle = line_pin_middle.value
    status_left = line_pin_left.value

    if status_middle:
        move.move(100, 'forward', 'no', 1)
    elif status_left:
        move.move(100, 'forward', 'right', 0.6)
    elif status_right:
        move.move(100, 'forward', 'left', 0.6)
    else:
        move.move(100, 'backward', 'no', 1)

if __name__ == '__main__':
    try:
        move.setup()  # Ensure motors are initialized
        while True:
            run()
            time.sleep(0.1)  # Small delay to reduce CPU usage
    except KeyboardInterrupt:
        move.destroy()