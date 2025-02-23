#!/usr/bin/env python3
# File name   : switch.py
# Description : Control HAT switches using gpiozero
# Product     : HAT
# Website     : www.gewbot.com
# Author      : William (modified by ChatGPT)
# Date        : 2018/08/22 (updated for gpiozero)

import time
from gpiozero import DigitalOutputDevice

# Define BCM pins for switches
PIN_SWITCH_1 = 5
PIN_SWITCH_2 = 6
PIN_SWITCH_3 = 13

# Create global DigitalOutputDevice objects for the switches (initially off)
switch1 = DigitalOutputDevice(PIN_SWITCH_1, active_high=True, initial_value=False)
switch2 = DigitalOutputDevice(PIN_SWITCH_2, active_high=True, initial_value=False)
switch3 = DigitalOutputDevice(PIN_SWITCH_3, active_high=True, initial_value=False)

def switchSetup():
    """
    Setup function for switches.
    In gpiozero, initialization is done on object creation.
    This function ensures all switches are off.
    """
    global switch1, switch2, switch3
    switch1.off()
    switch2.off()
    switch3.off()

def switch(port, status):
    """
    Set the switch state for a given port.
    :param port: Switch port (1, 2, or 3)
    :param status: 1 to turn on, 0 to turn off
    """
    if port == 1:
        if status == 1:
            switch1.on()
        elif status == 0:
            switch1.off()
    elif port == 2:
        if status == 1:
            switch2.on()
        elif status == 0:
            switch2.off()
    elif port == 3:
        if status == 1:
            switch3.on()
        elif status == 0:
            switch3.off()
    else:
        print('Wrong Command: Example -- switch(3, 1) to switch on port 3')

def set_all_switch_off():
    """Turn off all switches."""
    switch(1, 0)
    switch(2, 0)
    switch(3, 0)

if __name__ == "__main__":
    switchSetup()
    while True:
        switch(1, 1)
        switch(2, 1)
        switch(3, 1)
        print("Light on...")
        time.sleep(1)
        set_all_switch_off()
        print("Light off...")
        time.sleep(1)
