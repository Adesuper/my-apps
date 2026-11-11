# ==================================================================
#  SESSION 1  --  HELLO LIGHT
#  Make one LED blink. This is the "Hello world" of hardware.
#
#  Wiring (power the Pi OFF first):
#    GPIO17 (pin 11) -> 220 ohm resistor -> LED long leg (+)
#    LED short leg (-) -> GND (pin 9)
#
#  Run it:   python3 s1_blink.py      Stop it:  Ctrl + C
# ==================================================================

from gpiozero import LED
from time import sleep

light = LED(17)          # the LED is on GPIO17

print("Blinking! Press Ctrl+C to stop.")

while True:
    light.on()
    sleep(0.5)           # wait half a second
    light.off()
    sleep(0.5)

# TRY THIS:
#   1. Make it blink faster (change 0.5 to 0.1).
#   2. Blink S.O.S. in Morse code: 3 short, 3 long, 3 short.
#   3. Add a second LED on GPIO27 and make them take turns.
