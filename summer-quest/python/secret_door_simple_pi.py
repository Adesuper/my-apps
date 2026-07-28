# ==================================================================
#  SECRET DOOR -- STEP 1 (WARM-UP)  --  Raspberry Pi + Freenove kit
#  The easy version: NO screen yet. Just lights and a beep.
#  Do this first, then move on to secret_door_pi.py (adds the LCD).
#
#  GROWN-UP HELP NEEDED for the wiring. Power OFF the Pi before wiring.
#
#  Parts from the Freenove kit:
#    - 1 green LED + 1 red LED, each with a 220 ohm resistor
#    - 1 buzzer (active)
#    - breadboard + jumper wires
#
#  Wiring (BCM pin numbers):
#    Green LED (+ 220 ohm resistor):  GPIO17 (pin 11)  ->  LED  ->  GND
#    Red   LED (+ 220 ohm resistor):  GPIO27 (pin 13)  ->  LED  ->  GND
#    Buzzer:                          GPIO22 (pin 15)  ->  buzzer  ->  GND
#
#  Nothing to install -- gpiozero already comes with the Raspberry Pi.
# ==================================================================

from gpiozero import LED, Buzzer
from time import sleep

green  = LED(17)
red    = LED(27)
buzzer = Buzzer(22)

SECRET = "dragon"           # <-- change this to your own secret word!

code = input("Enter the secret word: ")

if code == SECRET:
    print("Correct! Green light on.")
    green.on()
    buzzer.on(); sleep(0.2); buzzer.off()   # a happy beep
    sleep(3)
    green.off()
else:
    print("Wrong word. Red light on.")
    red.on()
    sleep(3)
    red.off()

# TRY THIS:
#   - Add an elif for a "boss" code that beeps twice.
#   - When you're ready, wire the LCD and run secret_door_pi.py.
