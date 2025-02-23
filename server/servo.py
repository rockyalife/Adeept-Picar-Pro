#!/usr/bin/env python3
# File name   : servo.py
# Description : Control Servos using CircuitPython PCA9685 (Blinka)
# Author      : William (modified by ChatGPT)
# Date        : 2019/02/23 (updated for Raspberry Pi 5 with Blinka)

from __future__ import division
import time
import sys
import ultra

# CircuitPython imports
import board
import busio
import adafruit_pca9685

# Create the I2C object and initialize the PCA9685
# The PCA9685 is a PWM driver that can control up to 16 servos or LEDs.
# It communicates with the Raspberry Pi via the I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c, address=0x40)
pca.frequency = 50  # Set the PWM frequency to 50Hz, which is standard for servos

# Helper function to convert a value (0-4095) to a 16-bit duty_cycle
# The PCA9685 uses 16-bit values for PWM duty cycles.
def set_pwm(channel, value):
    # Convert value from 0-4095 to 0-65535
    duty = int(value * 65535 / 4095)
    pca.channels[channel].duty_cycle = duty

'''
Change these from 1 to 0 to reverse servos.
Calibration values (ranges) according to your application.
'''
pwm0_direction = 1
pwm1_direction = 1
pwm2_direction = 1
pwm3_direction = 1

# Calibration values for each channel
# These values define the initial, maximum, and minimum positions for each servo.
pwm0_init = 300
pwm0_max  = 450
pwm0_min  = 150
pwm0_pos  = pwm0_init

pwm1_init = 300
pwm1_max  = 480
pwm1_min  = 160
pwm1_pos  = pwm1_init

pwm2_init = 300
pwm2_max  = 500
pwm2_min  = 100
pwm2_pos  = pwm2_init

pwm3_init = 300
pwm3_max  = 500
pwm3_min  = 300
pwm3_pos  = pwm3_init

org_pos = 300  # Default position for the servos

# Function to perform a radar scan using the ultrasonic sensor
# This function moves the servo back and forth while taking distance measurements.
def radar_scan():
    global pwm0_pos
    scan_result = 'U: '
    scan_speed = 1
    if pwm0_direction:
        pwm0_pos = pwm0_max
        set_pwm(0, pwm0_pos)
        time.sleep(0.5)
        scan_result += str(ultra.checkdist()) + ' '
        while pwm0_pos > pwm0_min:
            pwm0_pos -= scan_speed
            set_pwm(0, pwm0_pos)
            scan_result += str(ultra.checkdist()) + ' '
        set_pwm(0, pwm0_init)
    else:
        pwm0_pos = pwm0_min
        set_pwm(0, pwm0_pos)
        time.sleep(0.5)
        scan_result += str(ultra.checkdist()) + ' '
        while pwm0_pos < pwm0_max:
            pwm0_pos += scan_speed
            set_pwm(0, pwm0_pos)
            scan_result += str(ultra.checkdist()) + ' '
        set_pwm(0, pwm0_init)
    return scan_result

# Function to control the range of a value
# This function ensures that a value stays within a specified range.
def ctrl_range(raw, max_genout, min_genout):
    if raw > max_genout:
        raw_output = max_genout
    elif raw < min_genout:
        raw_output = min_genout
    else:
        raw_output = raw
    return int(raw_output)

# Function to control the camera angle
# This function adjusts the camera angle based on the specified direction and angle.
def camera_ang(direction, ang):
    global org_pos
    # If "ang" is 'no', set a default value
    if ang == 'no':
        ang = 50
    # The logic below can be inverted according to the servo direction
    if look_direction:
        if direction == 'lookdown':
            org_pos += ang
            org_pos = ctrl_range(org_pos, look_max, look_min)
        elif direction == 'lookup':
            org_pos -= ang
            org_pos = ctrl_range(org_pos, look_max, look_min)
        elif direction == 'home':
            org_pos = 300
    else:
        if direction == 'lookdown':
            org_pos -= ang
            org_pos = ctrl_range(org_pos, look_max, look_min)
        elif direction == 'lookup':
            org_pos += ang
            org_pos = ctrl_range(org_pos, look_max, look_min)
        elif direction == 'home':
            org_pos = 300
    # Update all channels with the same value
    for ch in range(16):
        set_pwm(ch, org_pos)

# Function to move the servo to the left
def lookleft(speed):
    global pwm0_pos
    if pwm0_direction:
        pwm0_pos += speed
        pwm0_pos = ctrl_range(pwm0_pos, pwm0_max, pwm0_min)
        set_pwm(0, pwm0_pos)
    else:
        pwm0_pos -= speed
        pwm0_pos = ctrl_range(pwm0_pos, pwm0_max, pwm0_min)
        set_pwm(0, pwm0_pos)

# Function to move the servo to the right
def lookright(speed):
    global pwm0_pos
    if pwm0_direction:
        pwm0_pos -= speed
        pwm0_pos = ctrl_range(pwm0_pos, pwm0_max, pwm0_min)
        set_pwm(0, pwm0_pos)
    else:
        pwm0_pos += speed
        pwm0_pos = ctrl_range(pwm0_pos, pwm0_max, pwm0_min)
        set_pwm(0, pwm0_pos)

# Function to move the servo up
def up(speed):
    global pwm1_pos
    if pwm1_direction:
        pwm1_pos -= speed
        pwm1_pos = ctrl_range(pwm1_pos, pwm1_max, pwm1_min)
        set_pwm(1, pwm1_pos)
    else:
        pwm1_pos += speed
        pwm1_pos = ctrl_range(pwm1_pos, pwm1_max, pwm1_min)
        set_pwm(1, pwm1_pos)

# Function to move the servo down
def down(speed):
    global pwm1_pos
    if pwm1_direction:
        pwm1_pos += speed
        pwm1_pos = ctrl_range(pwm1_pos, pwm1_max, pwm1_min)
        set_pwm(1, pwm1_pos)
    else:
        pwm1_pos -= speed
        pwm1_pos = ctrl_range(pwm1_pos, pwm1_max, pwm1_min)
        set_pwm(1, pwm1_pos)

# Function to move the servo up (alternative)
def lookup(speed):
    global pwm2_pos
    if pwm2_direction:
        pwm2_pos -= speed
        pwm2_pos = ctrl_range(pwm2_pos, pwm2_max, pwm2_min)
        set_pwm(2, pwm2_pos)
    else:
        pwm2_pos += speed
        pwm2_pos = ctrl_range(pwm2_pos, pwm2_max, pwm2_min)
        set_pwm(2, pwm2_pos)

# Function to move the servo down (alternative)
def lookdown(speed):
    global pwm2_pos
    if pwm2_direction:
        pwm2_pos += speed
        pwm2_pos = ctrl_range(pwm2_pos, pwm2_max, pwm2_min)
        set_pwm(2, pwm2_pos)
    else:
        pwm2_pos -= speed
        pwm2_pos = ctrl_range(pwm2_pos, pwm2_max, pwm2_min)
        set_pwm(2, pwm2_pos)

# Function to grab an object
def grab(speed):
    global pwm3_pos
    if pwm3_direction:
        pwm3_pos -= speed
        pwm3_pos = ctrl_range(pwm3_pos, pwm3_max, pwm3_min)
        set_pwm(3, pwm3_pos)
    else:
        pwm3_pos += speed
        pwm3_pos = ctrl_range(pwm3_pos, pwm3_max, pwm3_min)
        set_pwm(3, pwm3_pos)
    print(pwm3_pos)

# Function to release an object
def loose(speed):
    global pwm3_pos
    if pwm3_direction:
        pwm3_pos += speed
        pwm3_pos = ctrl_range(pwm3_pos, pwm3_max, pwm3_min)
        set_pwm(3, pwm3_pos)
    else:
        pwm3_pos -= speed
        pwm3_pos = ctrl_range(pwm3_pos, pwm3_max, pwm3_min)
        set_pwm(3, pwm3_pos)
    print(pwm3_pos)

# Function to initialize the servos
def servo_init():
    set_pwm(0, pwm0_pos)
    set_pwm(1, pwm1_pos)
    set_pwm(2, pwm2_max)
    set_pwm(3, pwm3_pos)

# Function to reset all servos
def clean_all():
    # Recreate the PCA9685 object and reset the channels
    global pca
    pca = adafruit_pca9685.PCA9685(i2c, address=0x40)
    pca.frequency = 50
    for ch in range(16):
        set_pwm(ch, 0)

# Function to move the servos to the initial position
def ahead():
    global pwm0_pos, pwm1_pos
    set_pwm(0, pwm0_init)
    set_pwm(1, pwm1_max - 20)
    pwm0_pos = pwm0_init
    pwm1_pos = pwm1_max - 20

# Function to get the current direction of the servo
def get_direction():
    return (pwm0_pos - pwm0_init)

if __name__ == '__main__':
    while True:
        for i in range(0, 100):
            set_pwm(0, (300 + i))
            time.sleep(0.05)
        for i in range(0, 100):
            set_pwm(0, (400 - i))
            time.sleep(0.05)