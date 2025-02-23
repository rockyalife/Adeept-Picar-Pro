#!/usr/bin/env python3
# File name   : servo.py
# Description : Control lights with NeoPixels using gpiozero
# Author      : William (modified by ChatGPT)
# Date        : 2019/02/23 (updated for gpiozero)

import time
import threading
from rpi_ws281x import *
from gpiozero import DigitalOutputDevice 

class RobotLight(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.frontLight1 = DigitalOutputDevice(5)   # GPIO 5
        self.frontLight2 = DigitalOutputDevice(6)   # GPIO 6
        self.frontLight3 = DigitalOutputDevice(13)  # GPIO 13

        self.LED_COUNT = 16      # Number of LED pixels
        self.LED_PIN = 18        # GPIO pin 18 (PWM)
        self.LED_FREQ_HZ = 800000  # LED signal frequency in Hz
        self.LED_DMA = 10       # DMA channel
        self.LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT = False    # True to invert the signal
        self.LED_CHANNEL = 0       # PWM channel

        # Variables for light effects
        self.colorBreathR = 0
        self.colorBreathG = 0
        self.colorBreathB = 0
        self.breathSteps = 10

        self.lightMode = 'none'

        # Create NeoPixel object
        self.strip = Adafruit_NeoPixel(
            self.LED_COUNT,
            self.LED_PIN,
            self.LED_FREQ_HZ,
            self.LED_DMA,
            self.LED_INVERT,
            self.LED_BRIGHTNESS,
            self.LED_CHANNEL
        )
        self.strip.begin()

        super(RobotLight, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

    # Control color of LEDs
    def setColor(self, R, G, B):
        """Set the color of all LEDs in the strip."""
        color = Color(int(R), int(G), int(B))  # Use Color function from rpi_ws281x
        for i in range(self.LED_COUNT):  # Use LED_COUNT instead of strip.n
            self.strip.setPixelColor(i, color)  # Use setPixelColor method
        self.strip.show()

    def setSomeColor(self, R, G, B, ID):
        """Set color for specific LEDs."""
        color = Color(int(R), int(G), int(B))  # Use Color function
        for i in ID:
            self.strip.setPixelColor(i, color)  # Use setPixelColor method
        self.strip.show()

    def pause(self):
        """Pause any light effect."""
        self.lightMode = 'none'
        self.setColor(0, 0, 0)
        self.__flag.clear()

    def resume(self):
        """Resume light effect."""
        self.__flag.set()

    def police(self):
        """Start police mode light effect."""
        self.lightMode = 'police'
        self.resume()

    def policeProcessing(self):
        """Flash red and blue lights like police sirens."""
        while self.lightMode == 'police':
            for i in range(3):
                self.setSomeColor(0, 0, 255, [0, 1, 2])
                time.sleep(0.05)
                self.setSomeColor(0, 0, 0, [0, 1, 2])
                time.sleep(0.05)

            if self.lightMode != 'police':
                break

            time.sleep(0.1)

            for i in range(3):
                self.setSomeColor(255, 0, 0, [0, 1, 2])
                time.sleep(0.05)
                self.setSomeColor(0, 0, 0, [0, 1, 2])
                time.sleep(0.05)

            time.sleep(0.1)

    def breath(self, R_input, G_input, B_input):
        """Start breath effect (color fades in and out)."""
        self.lightMode = 'breath'
        self.colorBreathR = R_input
        self.colorBreathG = G_input
        self.colorBreathB = B_input
        self.resume()

    def breathProcessing(self):
        """Color fades in and out with breath effect."""
        while self.lightMode == 'breath':
            for i in range(0, self.breathSteps):
                if self.lightMode != 'breath':
                    break
                self.setColor(self.colorBreathR * i / self.breathSteps,
                              self.colorBreathG * i / self.breathSteps,
                              self.colorBreathB * i / self.breathSteps)
                time.sleep(0.03)

            for i in range(0, self.breathSteps):
                if self.lightMode != 'breath':
                    break
                self.setColor(self.colorBreathR - (self.colorBreathR * i / self.breathSteps),
                              self.colorBreathG - (self.colorBreathG * i / self.breathSteps),
                              self.colorBreathB - (self.colorBreathB * i / self.breathSteps))
                time.sleep(0.03)

    def frontLight(self, switch):
        """Control front lights."""
        if switch == 'on':
            self.frontLight1.on()
            self.frontLight2.on()
        elif switch == 'off':
            self.frontLight1.off()
            self.frontLight3.off()

    def switch(self, port, status):
        """Switch on/off for specific ports (front light ports)."""
        if port == 1:
            if status == 1:
                self.frontLight1.on()
            elif status == 0:
                self.frontLight1.off()
        elif port == 2:
            if status == 1:
                self.frontLight2.on()
            elif status == 0:
                self.frontLight2.off()
        elif port == 3:
            if status == 1:
                self.frontLight3.on()
            elif status == 0:
                self.frontLight3.off()
        else:
            print('Wrong Command: Example--switch(3, 1)->to switch on port3')

    def set_all_switch_off(self):
        """Turn off all switches."""
        self.switch(1, 0)
        self.switch(2, 0)
        self.switch(3, 0)

    def lightChange(self):
        """Change light effect based on mode."""
        if self.lightMode == 'none':
            self.pause()
        elif self.lightMode == 'police':
            self.policeProcessing()
        elif self.lightMode == 'breath':
            self.breathProcessing()

    def run(self):
        """Thread running the light changes."""
        while 1:
            self.__flag.wait()
            self.lightChange()

if __name__ == '__main__':
    RL = RobotLight()
    RL.start()
    RL.breath(70, 70, 255)  # Set breath color effect
    time.sleep(15)
    RL.pause()  # Pause effect after 15 seconds
    RL.frontLight('off')  # Turn off front light
    time.sleep(2)
    RL.police()  # Start police siren effects