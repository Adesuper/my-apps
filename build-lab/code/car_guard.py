# ==================================================================
#  LEVEL 2  --  CAR THAT WON'T CRASH (ultrasonic "eyes")
#  The car drives forward. When something is closer than 25 cm, it
#  stops, backs up a little and turns to find a free path.
#
#  Run it from the kit's  Code/Server  folder, after the kit's own
#  ultrasonic test works:   python3 car_guard.py      Stop: Ctrl + C
#  (Works with both kit versions, like car_dance.py.)
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

try:
    from ultrasonic import Ultrasonic
except ImportError:
    from Ultrasonic import Ultrasonic
eyes = Ultrasonic()

SPEED = 1200
SAFE_DISTANCE = 25      # centimetres

try:
    while True:
        distance = eyes.get_distance()
        print("Distance:", distance, "cm")
        if distance > SAFE_DISTANCE:
            drive(SPEED, SPEED, SPEED, SPEED)            # path is clear
        else:
            drive(0, 0, 0, 0)                            # too close!
            time.sleep(0.3)
            drive(-SPEED, -SPEED, -SPEED, -SPEED)        # back up
            time.sleep(0.4)
            drive(SPEED, SPEED, -SPEED, -SPEED)          # turn right
            time.sleep(0.5)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    drive(0, 0, 0, 0)

# TRY THIS:
#   1. Change SAFE_DISTANCE. What is the smallest number that still works?
#   2. Turn LEFT instead of right every second time.
#   3. Build a maze with boxes and see if the car finds the way out.
