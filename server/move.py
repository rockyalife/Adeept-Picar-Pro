#!/usr/bin/env python3
# File name   : move.py
# Description : Control Motor using gpiozero
# Product     : GWR
# Website     : www.gewbot.com
# Author      : William (modified by ChatGPT)
# Date        : 2019/07/24 (updated for gpiozero)

import time
from gpiozero import PWMOutputDevice, DigitalOutputDevice
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()
# Define motor pins (BCM numbering)
# Motor A: Enable on pin 4, Direction pins on 26 and 21
# Motor B: Enable on pin 17, Direction pins on 27 and 18
MOTOR_A_EN    = 4
MOTOR_B_EN    = 17

MOTOR_A_Pin1  = 26
MOTOR_A_Pin2  = 21
MOTOR_B_Pin1  = 27
MOTOR_B_Pin2  = 18

# Define directions constants
Dir_forward   = 0
Dir_backward  = 1

# Define motor direction flags (adjust these to reverse motor if needed)
left_forward  = 1
left_backward = 0

right_forward = 0
right_backward= 1

# Create gpiozero devices for Motor A
motor_a_enable = PWMOutputDevice(MOTOR_A_EN, frequency=1000)
motor_a_pin1 = DigitalOutputDevice(MOTOR_A_Pin1)
motor_a_pin2 = DigitalOutputDevice(MOTOR_A_Pin2)

# Create gpiozero devices for Motor B
motor_b_enable = PWMOutputDevice(MOTOR_B_EN, frequency=1000)
motor_b_pin1 = DigitalOutputDevice(MOTOR_B_Pin1)
motor_b_pin2 = DigitalOutputDevice(MOTOR_B_Pin2)

def motorStop():
    """Stop both motors."""
    print('Both motors stopping...')
    motor_a_pin1.off()
    motor_a_pin2.off()
    motor_b_pin1.off()
    motor_b_pin2.off()
    motor_a_enable.value = 0
    motor_b_enable.value = 0

def setup():
    """Initialize motor control (gpiozero devices are already created)."""
    motorStop()
    # No additional setup is required with gpiozero.

def motor_left(status, direction, speed):
    """
    Control left motor (Motor B).
    :param status: 0 to stop, 1 to run
    :param direction: Dir_forward or Dir_backward
    :param speed: 0-100 (percentage)
    """
    if status == 0:
        motor_b_pin1.off()
        motor_b_pin2.off()
        motor_b_enable.value = 0
    else:
        if direction == Dir_backward:
            motor_b_pin1.on()
            motor_b_pin2.off()
            motor_b_enable.value = speed / 100.0
        elif direction == Dir_forward:
            motor_b_pin1.off()
            motor_b_pin2.on()
            motor_b_enable.value = speed / 100.0

def motor_right(status, direction, speed):
    """
    Control right motor (Motor A).
    :param status: 0 to stop, 1 to run
    :param direction: Dir_forward or Dir_backward
    :param speed: 0-100 (percentage)
    """
    if status == 0:
        motor_a_pin1.off()
        motor_a_pin2.off()
        motor_a_enable.value = 0
    else:
        if direction == Dir_forward:
            motor_a_pin1.on()
            motor_a_pin2.off()
            motor_a_enable.value = speed / 100.0
        elif direction == Dir_backward:
            motor_a_pin1.off()
            motor_a_pin2.on()
            motor_a_enable.value = speed / 100.0
    return direction

def move(speed, direction, turn, radius=0.6):
    """
    Move the robot.
    :param speed: speed percentage (0-100)
    :param direction: 'forward', 'backward', or 'no'
    :param turn: 'right', 'left', or 'no'
    :param radius: turning radius factor (0 < radius <= 1)
    """
    if direction == 'forward':
        if turn == 'right':
            motor_left(0, left_backward, int(speed * radius))
            motor_right(1, right_forward, speed)
        elif turn == 'left':
            motor_left(1, left_forward, speed)
            motor_right(0, right_backward, int(speed * radius))
        else:
            motor_left(1, left_forward, speed)
            motor_right(1, right_forward, speed)
    elif direction == 'backward':
        if turn == 'right':
            motor_left(0, left_forward, int(speed * radius))
            motor_right(1, right_backward, speed)
        elif turn == 'left':
            motor_left(1, left_backward, speed)
            motor_right(0, right_forward, int(speed * radius))
        else:
            motor_left(1, left_backward, speed)
            motor_right(1, right_backward, speed)
    elif direction == 'no':
        if turn == 'right':
            motor_left(1, left_backward, speed)
            motor_right(1, right_forward, speed)
        elif turn == 'left':
            motor_left(1, left_forward, speed)
            motor_right(1, right_backward, speed)
        else:
            motorStop()
    else:
        pass

def destroy():
    """Stop motors and clean up."""
    motorStop()
    # With gpiozero, explicit cleanup is not required, but you can close devices if needed.
    motor_a_enable.close()
    motor_b_enable.close()
    motor_a_pin1.close()
    motor_a_pin2.close()
    motor_b_pin1.close()
    motor_b_pin2.close()

if __name__ == '__main__':
    try:
        print('Press Ctrl-C to end the program...')
        speed_set = 60
        setup()
        move(speed_set, 'forward', 'no', 0.8)
        time.sleep(1.3)
        motorStop()
        destroy()
    except KeyboardInterrupt:
        destroy()
