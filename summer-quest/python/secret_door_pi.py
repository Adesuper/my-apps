# ==================================================================
#  SECRET DOOR  --  Raspberry Pi + Freenove Starter Kit project
#  Type a secret code. The LCD, a green/red LED and a buzzer react
#  using the SAME if / else you learned on the computer.
#
#  GROWN-UP HELP NEEDED for the wiring. Power OFF the Pi before wiring.
#
#  Parts from the Freenove kit:
#    - LCD1602 (the I2C version, with 4 pins: GND VCC SDA SCL)
#    - 1 green LED + 1 red LED, each with a 220 ohm resistor
#    - 1 buzzer (active)
#    - breadboard + jumper wires
#
#  Before running:
#    1. Enable I2C:  sudo raspi-config  ->  Interface Options  ->  I2C  ->  Yes
#    2. Find the LCD address:  i2cdetect -y 1   (usually 0x27 or 0x3f)
#    3. Copy the file  LCD1602.py  from your Freenove kit's
#       "I2C LCD1602" lesson folder into THIS folder.
#
#  Wiring (BCM pin numbers):
#    LCD1602:  GND->GND   VCC->5V   SDA->GPIO2 (pin 3)   SCL->GPIO3 (pin 5)
#    Green LED (+ 220 ohm resistor):  GPIO17 (pin 11)  ->  LED  ->  GND
#    Red   LED (+ 220 ohm resistor):  GPIO27 (pin 13)  ->  LED  ->  GND
#    Buzzer:                          GPIO22 (pin 15)  ->  buzzer  ->  GND
# ==================================================================

from gpiozero import LED, Buzzer
from time import sleep
import LCD1602               # comes from your Freenove kit

# --- the parts, connected to their pins ---
green  = LED(17)
red    = LED(27)
buzzer = Buzzer(22)

SECRET = "dragon"           # <-- change this to your own secret word!

# --- turn the little screen on ---
LCD1602.init(0x27, 1)       # use YOUR address from i2cdetect if not 0x27
LCD1602.clear()
LCD1602.write(0, 0, "Secret Door")
LCD1602.write(0, 1, "Type the code...")

# --- ask, then let if / else decide ---
code = input("Enter the secret word: ")

if code == SECRET:
    LCD1602.clear()
    LCD1602.write(0, 0, "Correct!")
    LCD1602.write(0, 1, "Welcome in :)")
    green.on()
    buzzer.on(); sleep(0.2); buzzer.off()   # a happy beep
    sleep(3)
    green.off()
else:
    LCD1602.clear()
    LCD1602.write(0, 0, "Wrong word!")
    LCD1602.write(0, 1, "Door stays shut")
    red.on()
    sleep(3)
    red.off()

LCD1602.clear()

# TRY THIS (once it works):
#   - Add an elif for a "master" code that shows "Hello boss!".
#   - Give 3 tries using a for loop before it locks.
#   - Swap the buzzer beep to play twice when correct.
