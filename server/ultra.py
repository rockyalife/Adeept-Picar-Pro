#!/usr/bin/env python3
# File name   : Ultrasonic.py
# Description : Distance detection and tracking using gpiozero's DistanceSensor
# Website     : www.gewbot.com
# Author      : William (modified by ChatGPT)
# Date        : 2019/02/23 (updated for gpiozero)

import sys
sys.path.append('/usr/lib/python3/dist-packages')

from gpiozero import DistanceSensor
import time
# Configure o sensor ultrassônico:
# Trigger conectado ao pino 11 e Echo ao pino 8
# max_distance define a distância máxima que o sensor irá medir (em metros)
sensor = DistanceSensor(echo=8, trigger=11, max_distance=4)

def checkdist():
    # DistanceSensor.distance retorna a distância em metros.
    # Se preferir em metros, apenas arredonde:
    return round(sensor.distance, 2)

if __name__ == '__main__':
    while True:
        print(checkdist())
        time.sleep(1)
