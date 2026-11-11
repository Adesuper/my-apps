# ==================================================================
#  SESSION 4  --  ROOM SCREEN (temperature + humidity on the LCD)
#
#  Wiring (power the Pi OFF first):
#    DHT11 sensor:  VCC (+) -> 3.3V (pin 1)
#                   DATA    -> GPIO23 (pin 16)
#                   GND (-) -> GND (pin 20)
#    LCD1602 (I2C): GND -> GND (pin 9)   VCC -> 5V (pin 4)
#                   SDA -> GPIO2 (pin 3) SCL -> GPIO3 (pin 5)
#
#  Before running (once):
#    1. Turn on I2C:  sudo raspi-config -> Interface Options -> I2C -> Yes
#    2. Find the screen address:  i2cdetect -y 1   (usually 27 or 3f)
#    3. Copy these two files from your Freenove kit's code folders into
#       THIS folder:  LCD1602.py   (from the "I2C LCD1602" lesson)
#                     Freenove_DHT.py  (from the "DHT11" lesson)
#    4. Open the kit's DHT11 example. If it says  DHTPin = 11,  the kit
#       counts pins by board position: set DHT_PIN = 16 below.
#       If it says  DHTPin = 17  (a GPIO number), keep DHT_PIN = 23.
#
#  Run it:   python3 s4_room_screen.py      Stop it:  Ctrl + C
# ==================================================================

import time
import LCD1602
import Freenove_DHT as DHT

DHT_PIN = 23          # see step 4 above
LCD_ADDRESS = 0x27    # use YOUR address from i2cdetect (0x27 or 0x3f)

dht = DHT.DHT(DHT_PIN)
LCD1602.init(LCD_ADDRESS, 1)
LCD1602.clear()


def read_room():
    """Ask the sensor up to 15 times. Returns (temperature, humidity)."""
    for attempt in range(15):
        if dht.readDHT11() == dht.DHTLIB_OK:
            return dht.temperature, dht.humidity
        time.sleep(0.1)
    return None, None


try:
    while True:
        temp, hum = read_room()
        LCD1602.clear()
        if temp is None:
            LCD1602.write(0, 0, "Sensor busy...")
        else:
            LCD1602.write(0, 0, "Temp: %d C" % temp)
            LCD1602.write(0, 1, "Humidity: %d %%" % hum)
            print("Temperature:", temp, "C    Humidity:", hum, "%")
        time.sleep(2)
except KeyboardInterrupt:
    LCD1602.clear()

# TRY THIS:
#   1. Breathe on the sensor. What happens to the humidity? Why?
#   2. Show "Too hot!" on the screen when the temperature is above 25.
#   3. If it shows an error, open the kit's DHT11 example and compare
#      how it reads the sensor (some kit versions use other names).
