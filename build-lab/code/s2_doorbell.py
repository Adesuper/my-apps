# ==================================================================
#  SESSION 2  --  MY DOORBELL
#  Press the button: the buzzer rings and the light turns on.
#
#  Wiring (power the Pi OFF first):
#    LED:     GPIO17 (pin 11) -> 220 ohm resistor -> LED (+) ... LED (-) -> GND
#    Button:  one leg -> GPIO18 (pin 12), the other leg -> GND (pin 14)
#    Buzzer:  GPIO22 (pin 15). Build it the way your Freenove kit's
#             "Doorbell / Active buzzer" lesson shows (it uses a small
#             transistor so the buzzer is loud and the Pi stays safe).
#
#  Run it:   python3 s2_doorbell.py      Stop it:  Ctrl + C
# ==================================================================

from gpiozero import Button, Buzzer, LED
from signal import pause

bell = Button(18)
buzzer = Buzzer(22)
light = LED(17)

def ding():
    print("Ding dong! Someone is at the door!")
    light.on()
    buzzer.beep(on_time=0.2, off_time=0.1, n=2, background=True)

def done():
    light.off()

bell.when_pressed = ding      # run ding() when the button goes down
bell.when_released = done     # run done() when it comes back up

print("Doorbell ready. Press the button!")
pause()                       # wait forever for button presses

# TRY THIS:
#   1. Count the visitors: add a number that goes up at each ding.
#   2. Make a "secret knock": 3 quick presses plays a special tune.
