#!/usr/bin/python3
# File name   : setup.py
# Author      : Adeept (modified by ChatGPT)
# Date        : 2020/3/14 (modified for Raspberry Pi OS on Pi 5)
#
# This script sets up the environment for Adeept Picar Pro.
# It installs necessary dependencies, configures hardware, and sets up a systemd service for startup.
#
# Note: Run this script as root (e.g., with sudo).

import os
import sys
import subprocess

# Ensure the script is run as root
if os.geteuid() != 0:
    sys.exit("This script must be run as root. Please run with sudo.")
    
# Get the original user who invoked sudo, if available
home_dir = os.path.expanduser("~" + os.environ.get("SUDO_USER", ""))
# Fallback to current user's home directory if SUDO_USER is not set
if not home_dir.strip("~"):
    home_dir = os.path.expanduser("~")

# Helper function to run commands with retries
def run_command(command, retries=3):
    for attempt in range(retries):
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            return True
        else:
            print(f"Attempt {attempt + 1} failed for: {command}")
    return False

# Function to replace lines in a file that start with a specific string.
def replace_num(file, initial, new_num):
    newline = ""
    try:
        with open(file, "r") as f:
            for line in f.readlines():
                if line.startswith(initial):
                    line = new_num + "\n"
                newline += line
        with open(file, "w") as f:
            f.write(newline)
    except Exception as e:
        print(f"Error replacing text in {file}: {e}")

# Determine current script directory
curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

# Update system packages and clean up
run_command("apt-get update")
os.system("apt-get purge -y wolfram-engine")
os.system("apt-get purge -y libreoffice*")
os.system("apt-get -y clean")
os.system("apt-get -y autoremove")

# Upgrade pip (using --break-system-packages to bypass PEP 668 restrictions)
run_command("pip3 install --break-system-packages -U pip")

# Install required system packages
run_command("apt-get install -y python-dev-is-python3 python3-pip libfreetype6-dev libjpeg-dev build-essential")
run_command("apt-get install -y i2c-tools")
run_command("apt-get install -y python3-opencv")
run_command("apt-get install -y python3-smbus")
run_command("apt-get install -y libhdf5-dev")
run_command("apt-get install -y util-linux procps hostapd iproute2 iw haveged dnsmasq")

# Install Python packages with pip using the --break-system-packages flag
run_command("pip3 install --break-system-packages --upgrade luma.oled")
run_command("pip3 install --break-system-packages adafruit-pca9685")
run_command("pip3 install --break-system-packages rpi_ws281x")
run_command("pip3 install --break-system-packages mpu6050-raspberrypi")
run_command("pip3 install --break-system-packages flask")
run_command("pip3 install --break-system-packages flask_cors")
run_command("pip3 install --break-system-packages websockets")
run_command("pip3 install --break-system-packages numpy")
run_command("pip3 install --break-system-packages imutils zmq pybase64 psutil")
run_command("pip3 install --break-system-packages RPi.GPIO")
run_command("pip3 install adafruit-blinka adafruit-circuitpython-pca9685")

# Modify /boot/config.txt to enable I2C and set camera start_x flag
try:
    replace_num("/boot/config.txt", "#dtparam=i2c_arm=on", "dtparam=i2c_arm=on\nstart_x=1")
except Exception as e:
    print("Error updating /boot/config.txt:", e)

# Clone the create_ap repository if not already present
if not os.path.exists("create_ap"):
    run_command("git clone https://github.com/oblique/create_ap")
else:
    print("Directory 'create_ap' already exists; skipping clone.")

# Install create_ap (attempt installation from two possible directories)
try:
    run_command("cd " + thisPath + "/create_ap && make install")
except Exception as e:
    print("Error installing create_ap from", thisPath + "/create_ap:", e)

try:
    run_command(f"cd {home_dir}/create_ap && make install")
except Exception as e:
    print("Error installing create_ap from /home/gocar/create_ap:", e)

# Create startup script
startup_path = f"{home_dir}/startup.sh"
try:
    run_command(f"touch {startup_path}")
    with open(startup_path, 'w') as f:
        # Choose your desired startup command (example uses webServer.py)
        f.write("#!/bin/sh\nsudo python3 " + thisPath + "/server/webServer.py")
    os.system(f"chmod +x {startup_path}")
except Exception as e:
    print("Failure creating startup.sh:", e)

# Create a systemd service to run the startup script on boot
service_file = "/etc/systemd/system/adeept-picar.service"
service_content = f"""[Unit]
Description=Startup script for Adeept Picar Pro
After=multi-user.target

[Service]
Type=idle
ExecStart={startup_path} start

[Install]
WantedBy=multi-user.target
"""

try:
    with open(service_file, "w") as f:
        f.write(service_content)
    run_command("systemctl daemon-reload")
    run_command("systemctl enable adeept-picar.service")
except Exception as e:
    print("Failure while creating systemd service:", e)

# Fix potential conflict with onboard Raspberry Pi audio
try:
    run_command("touch /etc/modprobe.d/snd-blacklist.conf")
    with open("/etc/modprobe.d/snd-blacklist.conf", 'w') as f:
        f.write("blacklist snd_bcm2835")
except Exception as e:
    print("Error configuring audio blacklist:", e)

print("The program on Raspberry Pi has been installed and configured.")
print("You can now power off the Raspberry Pi to install the camera and driver board (Robot HAT).")
print("After powering on, the startup script will run automatically.")
print("Rebooting now...")
run_command("reboot")
