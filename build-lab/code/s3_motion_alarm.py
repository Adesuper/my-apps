# ==================================================================
#  SESSION 3  --  ROOM GUARD (motion alarm)
#  When someone walks into the room, the red light flashes and the
#  buzzer beeps.
#
#  Wiring (power the Pi OFF first):
#    PIR motion sensor (HC-SR501):  VCC -> 5V (pin 2)
#                                   OUT -> GPIO4 (pin 7)
#                                   GND -> GND (pin 6)
#    Red LED:  GPIO27 (pin 13) -> 220 ohm resistor -> LED (+) ... LED (-) -> GND
#    Buzzer:   GPIO22 (pin 15), same as session 2
#
#  Run it:   python3 s3_motion_alarm.py      Stop it:  Ctrl + C
# ==================================================================

from gpiozero import MotionSensor, LED, Buzzer
from time import sleep, strftime

pir = MotionSensor(4)
alarm = LED(27)
buzzer = Buzzer(22)

print("Warming up the motion sensor (30 seconds). Stay still...")
sleep(30)
print("Room guard is ON. Walk in front of the sensor!")

count = 0
while True:
    pir.wait_for_motion()
    count = count + 1
    print("Intruder alert number", count, "at", strftime("%H:%M:%S"))
    alarm.blink(on_time=0.1, off_time=0.1)
    buzzer.beep(on_time=0.1, off_time=0.1, n=5, background=True)

    pir.wait_for_no_motion()
    alarm.off()
    print("All clear.")

# TRY THIS:
#   1. Only beep for the first 3 alerts, then just flash the light.
#   2. Add the button from session 2 as an ON/OFF switch for the guard.
#
# The sensor has two small orange knobs: one changes how far it sees,
# the other how long it stays "on". Experiment with a screwdriver!
