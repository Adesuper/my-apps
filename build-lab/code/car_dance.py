# ==================================================================
#  LEVEL 2  --  MY ROBOT CAR DANCE (Israel's own program)
#  Run this on the car, from the kit's  Code/Server  folder, AFTER the
#  kit's own motor test works. Put the car on the floor with space
#  around it (or lift it so the wheels spin in the air the first time).
#
#  Freenove kits come in two versions. This program works with both:
#    newer kits have  motor.py  with  Ordinary_Car / set_motor_model
#    older kits have  Motor.py  with  Motor / setMotorModel
#
#  Run it:   python3 car_dance.py
# ==================================================================

import time

try:
    from motor import Ordinary_Car
    _car = Ordinary_Car()
    drive = _car.set_motor_model
except ImportError:
    from Motor import Motor
    _car = Motor()
    drive = _car.setMotorModel

SPEED = 1500        # 0 = stopped, 4095 = full speed. Start slow!

# the 4 numbers are: left-front, left-back, right-front, right-back


def forward(seconds):
    drive(SPEED, SPEED, SPEED, SPEED)
    time.sleep(seconds)


def backward(seconds):
    drive(-SPEED, -SPEED, -SPEED, -SPEED)
    time.sleep(seconds)


def spin_left(seconds):
    drive(-SPEED, -SPEED, SPEED, SPEED)
    time.sleep(seconds)


def spin_right(seconds):
    drive(SPEED, SPEED, -SPEED, -SPEED)
    time.sleep(seconds)


def stop(seconds=0.5):
    drive(0, 0, 0, 0)
    time.sleep(seconds)


try:
    print("Let's dance!")
    forward(1)
    stop()
    spin_left(0.8)
    stop()
    spin_right(0.8)
    stop()
    backward(1)
    stop()
    for wiggle in range(3):        # wiggle 3 times
        spin_left(0.2)
        spin_right(0.2)
    print("Ta-da!")
finally:
    drive(0, 0, 0, 0)              # always stop the motors at the end

# TRY THIS:
#   1. Make the car draw a square: forward, turn, 4 times (use a for loop).
#   2. Find how long spin_left must be to turn exactly a quarter turn.
#   3. Write your own dance and perform it to music for the family!
