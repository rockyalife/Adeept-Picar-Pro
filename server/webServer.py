#!/usr/bin/env python
# File name   : server.py
# Production  : GWR
# Website     : www.adeept.com
# Author      : William (modified by ChatGPT for CircuitPython PCA9685)
# Date        : 2020/03/17 (modified for Raspberry Pi 5 with Blinka)

import time
import threading
import os
import info
import socket

# Import CircuitPython I2C libraries; they will be used by RPIservo.
import board
import busio

# Initialize I2C for use by our updated RPIservo module
i2c = busio.I2C(board.SCL, board.SDA)

# Now import our updated RPIservo (which uses adafruit-circuitpython-pca9685)
import RPIservo

import move
import functions
import robotLight
import switch

# Websocket and JSON handling
import asyncio
import websockets
import json
import app

# OLED setup
OLED_connection = 1
try:
    import OLED
    screen = OLED.OLED_ctrl()
    screen.start()
    screen.screen_show(1, 'ADEEPT.COM')
except Exception as e:
    OLED_connection = 0
    print('OLED disconnected:', e)

mark_test = 0
functionMode = 0
speed_set = 100
rad = 0.5
turnWiggle = 60

# Initialize servo controllers from our updated RPIservo module
scGear = RPIservo.ServoCtrl()
scGear.moveInit()

P_sc = RPIservo.ServoCtrl()
P_sc.start()

T_sc = RPIservo.ServoCtrl()
T_sc.start()

H_sc = RPIservo.ServoCtrl()
H_sc.start()

G_sc = RPIservo.ServoCtrl()
G_sc.start()

modeSelect = 'PT'

# Save initial PWM positions
init_pwm = []
for i in range(16):
    init_pwm.append(scGear.initPos[i])

fuc = functions.Functions()
fuc.start()

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

def servoPosInit():
    scGear.initConfig(0, init_pwm[0], 1)
    P_sc.initConfig(1, init_pwm[1], 1)
    T_sc.initConfig(2, init_pwm[2], 1)
    H_sc.initConfig(3, init_pwm[3], 1)
    G_sc.initConfig(4, init_pwm[4], 1)

def replace_num(initial, new_num):
    newline = ""
    str_num = str(new_num)
    with open(thisPath + "/RPIservo.py", "r") as f:
        for line in f.readlines():
            if line.find(initial) == 0:
                line = initial + "%s" % (str_num + "\n")
            newline += line
    with open(thisPath + "/RPIservo.py", "w") as f:
        f.write(newline)

def FPV_thread():
    global fpv
    fpv = FPV.FPV()
    fpv.capture_thread(addr[0])

def ap_thread():
    os.system("sudo create_ap wlan0 eth0 Adeept_Robot 12345678")

def functionSelect(command_input, response):
    global functionMode
    if command_input == 'scan':
        if OLED_connection:
            screen.screen_show(5, 'SCANNING')
        if modeSelect == 'PT':
            radar_send = fuc.radarScan()
            print(radar_send)
            response['title'] = 'scanResult'
            response['data'] = radar_send
            time.sleep(0.3)
    elif command_input == 'findColor':
        if OLED_connection:
            screen.screen_show(5, 'FindColor')
        if modeSelect == 'PT':
            flask_app.modeselect('findColor')
    elif command_input == 'motionGet':
        if OLED_connection:
            screen.screen_show(5, 'MotionGet')
        flask_app.modeselect('watchDog')
    elif command_input == 'stopCV':
        flask_app.modeselect('none')
        switch.switch(1, 0)
        switch.switch(2, 0)
        switch.switch(3, 0)
    elif command_input == 'police':
        if OLED_connection:
            screen.screen_show(5, 'POLICE')
        RL.police()
    elif command_input == 'policeOff':
        RL.pause()
        move.motorStop()
    elif command_input == 'automatic':
        if OLED_connection:
            screen.screen_show(5, 'Automatic')
        if modeSelect == 'PT':
            fuc.automatic()
        else:
            fuc.pause()
    elif command_input == 'automaticOff':
        fuc.pause()
        move.motorStop()
    elif command_input == 'trackLine':
        fuc.trackLine()
        if OLED_connection:
            screen.screen_show(5, 'TrackLine')
    elif command_input == 'trackLineOff':
        fuc.pause()

def switchCtrl(command_input, response):
    if 'Switch_1_on' in command_input:
        switch.switch(1, 1)
    elif 'Switch_1_off' in command_input:
        switch.switch(1, 0)
    elif 'Switch_2_on' in command_input:
        switch.switch(2, 1)
    elif 'Switch_2_off' in command_input:
        switch.switch(2, 0)
    elif 'Switch_3_on' in command_input:
        switch.switch(3, 1)
    elif 'Switch_3_off' in command_input:
        switch.switch(3, 0)

def robotCtrl(command_input, response):
    if command_input == 'forward':
        move.move(speed_set, 'forward', 'no', rad)
    elif command_input == 'backward':
        move.move(speed_set, 'backward', 'no', rad)
    elif 'DS' in command_input:
        move.move(speed_set, 'no', 'no', rad)
    elif command_input == 'left':
        scGear.moveAngle(0, turnWiggle)
    elif command_input == 'right':
        scGear.moveAngle(0, -turnWiggle)
    elif 'TS' in command_input:
        scGear.moveServoInit([0])
    elif command_input == 'lookleft':
        P_sc.singleServo(1, 1, 3)
    elif command_input == 'lookright':
        P_sc.singleServo(1, -1, 3)
    elif command_input == 'LRstop':
        P_sc.stopWiggle()
    elif command_input == 'armup':
        T_sc.singleServo(2, 1, 3)
    elif command_input == 'armdown':
        T_sc.singleServo(2, -1, 3)
    elif command_input == 'armstop':
        T_sc.stopWiggle()
    elif command_input == 'handup':
        H_sc.singleServo(3, 1, 3)
    elif command_input == 'handdown':
        H_sc.singleServo(3, -1, 3)
    elif command_input == 'HAstop':
        H_sc.stopWiggle()
    elif command_input == 'grab':
        G_sc.singleServo(4, -1, 3)
    elif command_input == 'loose':
        G_sc.singleServo(4, 1, 3)
    elif command_input == 'stop':
        G_sc.stopWiggle()
    elif command_input == 'home':
        P_sc.moveServoInit([1])
        T_sc.moveServoInit([2])
        H_sc.moveServoInit([3])
        G_sc.moveServoInit([4])

def setPWM(data):
    global init_pwm
    action = data.split()[0]
    PWMNum = int(data.split()[1])
    if action == 'SiLeft':
        init_pwm[PWMNum] += 1
        scGear.setPWM(PWMNum, init_pwm[PWMNum])
    elif action == 'SiRight':
        init_pwm[PWMNum] -= 1
        scGear.setPWM(PWMNum, init_pwm[PWMNum])
    elif action == 'PWMMS':
        scGear.initConfig(PWMNum, init_pwm[PWMNum], 1)
        replace_num('init_pwm' + str(PWMNum) + ' = ', init_pwm[PWMNum])

def configPWM(command_input, response):
    global init_pwm
    if 'SiLeft' in command_input or 'SiRight' in command_input or 'PWMMS' in command_input:
        setPWM(command_input)
    elif command_input == 'PWMINIT':
        servoPosInit()
    elif command_input == 'PWMD':
        init_pwm0, init_pwm1, init_pwm2, init_pwm3, init_pwm4 = 300, 300, 300, 300, 300
        scGear.initConfig(0, init_pwm0, 1)
        replace_num('init_pwm0 = ', 300)
        P_sc.initConfig(1, 300, 1)
        replace_num('init_pwm1 = ', 300)
        T_sc.initConfig(2, 300, 1)
        replace_num('init_pwm2 = ', 300)
        H_sc.initConfig(3, 300, 1)
        replace_num('init_pwm3 = ', 300)
        G_sc.initConfig(4, 300, 1)
        replace_num('init_pwm4 = ', 300)
        for i in range(5, 16):
            replace_num('init_pwm' + str(i) + ' = ', 300)

def wifi_check():
    global mark_test
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ipaddr_check = s.getsockname()[0]
        s.close()
        print(ipaddr_check)
        if OLED_connection:
            screen.screen_show(2, 'IP:' + ipaddr_check)
            screen.screen_show(3, 'AP MODE OFF')
        mark_test = 1  
    except:
        if mark_test == 1:
            mark_test = 0
            move.destroy()
            scGear.moveInit()
        ap_threading = threading.Thread(target=ap_thread)
        ap_threading.setDaemon(True)
        ap_threading.start()
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 10%')
        RL.setColor(0, 16, 50)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 30%')
        RL.setColor(0, 16, 100)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 50%')
        RL.setColor(0, 16, 150)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 70%')
        RL.setColor(0, 16, 200)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 90%')
        RL.setColor(0, 16, 255)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 100%')
        RL.setColor(35, 255, 35)
        if OLED_connection:
            screen.screen_show(2, 'IP:192.168.12.1')
            screen.screen_show(3, 'AP MODE ON')

async def check_permit(websocket):
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await websocket.send(response_str)

async def recv_msg(websocket):
    global speed_set, modeSelect
    move.setup()
    direction_command = 'no'
    turn_command = 'no'
    while True: 
        response = {
            'status': 'ok',
            'title': '',
            'data': None
        }
        data = await websocket.recv()
        try:
            data = json.loads(data)
        except Exception as e:
            print('not A JSON')
        if not data:
            continue
        if isinstance(data, str):
            robotCtrl(data, response)
            switchCtrl(data, response)
            functionSelect(data, response)
            configPWM(data, response)
            if data == 'get_info':
                response['title'] = 'get_info'
                response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]
            if 'wsB' in data:
                try:
                    set_B = data.split()
                    speed_set = int(set_B[1])
                except:
                    pass
            elif data == 'AR':
                modeSelect = 'AR'
                screen.screen_show(4, 'ARM MODE ON')
                try:
                    fpv.changeMode('ARM MODE ON')
                except:
                    pass
            elif data == 'PT':
                modeSelect = 'PT'
                screen.screen_show(4, 'PT MODE ON')
                try:
                    fpv.changeMode('PT MODE ON')
                except:
                    pass
            elif data == 'CVFL':
                flask_app.modeselect('findlineCV')
            elif 'CVFLColorSet' in data:
                color = int(data.split()[1])
                flask_app.camera.colorSet(color)
            elif 'CVFLL1' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_1(pos)
            elif 'CVFLL2' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_2(pos)
            elif 'CVFLSP' in data:
                err = int(data.split()[1])
                flask_app.camera.errorSet(err)
            elif 'defEC' in data:
                fpv.defaultExpCom()
        elif isinstance(data, dict):
            if data['title'] == "findColorSet":
                color = data['data']
                flask_app.colorFindSet(color[0], color[1], color[2])
        if not functionMode:
            if OLED_connection:
                screen.screen_show(5, 'Functions OFF')
        print(data)
        response = json.dumps(response)
        await websocket.send(response)

async def main_logic(websocket, path):
    await check_permit(websocket)
    await recv_msg(websocket)

def test_Network_Connection():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("1.1.1.1", 80))
            s.close()
        except:
            move.destroy()
        time.sleep(0.5)

if __name__ == '__main__':
    switch.switchSetup()
    switch.set_all_switch_off()
    HOST = ''
    PORT = 10223
    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    global flask_app
    flask_app = app.webapp()
    flask_app.startthread()
    
    """ 
    If the Raspberry Pi is disconnected from the Internet, stop the car from moving.
    Reconnect to the network, you can continue to control the car.
    If you need this function, please enable the following three lines of code.
    Note: The program will additionally occupy the running memory of the Raspberry Pi.
    """
    # testNC_threading=threading.Thread(target=test_Network_Connection)
    # testNC_threading.setDaemon(False)
    # testNC_threading.start()                                     


    try:
        RL = robotLight.RobotLight()
        RL.start()
        RL.breath(70, 70, 255)
    except:
        print('Use "sudo pip3 install rpi_ws281x" to install WS_281x package')
        pass
    while True:
        wifi_check()
        try:
            start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
            asyncio.get_event_loop().run_until_complete(start_server)
            print('waiting for connection...')
            break
        except Exception as e:
            print(e)
            RL.setColor(0, 0, 0)
        try:
            RL.setColor(0, 80, 255)
        except:
            pass
    try:
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)
        RL.setColor(0, 0, 0)
        move.destroy()
