# ==================================================================
#  SESSION 5  --  SMART ROOM: control it from the phone!
#  Everything from sessions 1 to 4 together, plus a web page that
#  any phone on the home Wi-Fi can open.
#
#  Wiring: keep everything from sessions 1-4 plugged in:
#    light LED GPIO17 | alarm LED GPIO27 | buzzer GPIO22 | button GPIO18
#    motion sensor GPIO4 | DHT11 GPIO23 | LCD on SDA/SCL
#
#  Needs: Flask (already on Raspberry Pi OS; if not:
#         sudo apt install python3-flask)
#         and LCD1602.py + Freenove_DHT.py in this folder (session 4).
#
#  Run it:   python3 s5_smart_room.py
#  Find the Pi's address:   hostname -I     (example: 192.168.1.42)
#  On the phone (same Wi-Fi), open:   http://192.168.1.42:5000
# ==================================================================

import threading
import time
from flask import Flask, redirect
from gpiozero import LED, Buzzer, MotionSensor, Button
import LCD1602
import Freenove_DHT as DHT

ROOM_NAME = "Israel's Smart Room"   # <-- name your room!
DHT_PIN = 23                        # same as session 4
LCD_ADDRESS = 0x27                  # same as session 4

light = LED(17)
alarm = LED(27)
buzzer = Buzzer(22)
pir = MotionSensor(4)
bell = Button(18)
dht = DHT.DHT(DHT_PIN)

state = {"temp": None, "hum": None, "guard": True,
         "motions": 0, "last_motion": "none yet", "last_bell": "none yet"}


def sensor_loop():
    """Every 3 seconds: read the room and update the little screen."""
    while True:
        for attempt in range(15):
            if dht.readDHT11() == dht.DHTLIB_OK:
                state["temp"], state["hum"] = dht.temperature, dht.humidity
                break
            time.sleep(0.1)
        LCD1602.clear()
        if state["temp"] is not None:
            LCD1602.write(0, 0, "Temp: %d C" % state["temp"])
            LCD1602.write(0, 1, "Guard: %s" % ("ON" if state["guard"] else "off"))
        time.sleep(3)


def on_motion():
    state["motions"] += 1
    state["last_motion"] = time.strftime("%H:%M:%S")
    if state["guard"]:
        alarm.blink(on_time=0.1, off_time=0.1, n=10, background=True)
        buzzer.beep(on_time=0.1, off_time=0.1, n=5, background=True)


def on_bell():
    state["last_bell"] = time.strftime("%H:%M:%S")
    buzzer.beep(on_time=0.2, off_time=0.1, n=2, background=True)


pir.when_motion = on_motion
bell.when_pressed = on_bell

app = Flask(__name__)

STYLE = ("body{font-family:sans-serif;max-width:480px;margin:auto;padding:16px;"
         "background:#101735;color:#fff} .box{background:#24318a;border-radius:16px;"
         "padding:14px;margin:10px 0;font-size:20px} a.btn{display:inline-block;"
         "padding:14px 20px;margin:6px 6px 0 0;border-radius:12px;background:#ffc93c;"
         "color:#101735;font-weight:bold;text-decoration:none;font-size:18px}")


@app.route("/")
def home():
    temp = "--" if state["temp"] is None else "%d &deg;C" % state["temp"]
    hum = "--" if state["hum"] is None else "%d %%" % state["hum"]
    return ("<!doctype html><html><head><meta name='viewport' content='width=device-width'>"
            "<meta http-equiv='refresh' content='5'><title>Smart Room</title>"
            "<style>" + STYLE + "</style></head><body>"
            "<h1>" + ROOM_NAME + "</h1>"
            "<div class='box'>Temperature: <b>" + temp + "</b><br>Humidity: <b>" + hum + "</b></div>"
            "<div class='box'>Light: <b>" + ("ON" if light.is_lit else "off") + "</b><br>"
            "<a class='btn' href='/light/on'>Light ON</a><a class='btn' href='/light/off'>Light OFF</a></div>"
            "<div class='box'>Room guard: <b>" + ("ON" if state["guard"] else "off") + "</b><br>"
            "Motion seen: " + str(state["motions"]) + " times (last: " + state["last_motion"] + ")<br>"
            "<a class='btn' href='/guard/on'>Guard ON</a><a class='btn' href='/guard/off'>Guard OFF</a></div>"
            "<div class='box'>Doorbell last rang: " + state["last_bell"] + "<br>"
            "<a class='btn' href='/beep'>Beep from my phone</a></div>"
            "</body></html>")


@app.route("/light/<what>")
def set_light(what):
    if what == "on":
        light.on()
    else:
        light.off()
    return redirect("/")


@app.route("/guard/<what>")
def set_guard(what):
    state["guard"] = (what == "on")
    return redirect("/")


@app.route("/beep")
def beep():
    buzzer.beep(on_time=0.1, off_time=0.1, n=3, background=True)
    return redirect("/")


if __name__ == "__main__":
    LCD1602.init(LCD_ADDRESS, 1)
    threading.Thread(target=sensor_loop, daemon=True).start()
    print("Smart Room is running! On the phone open  http://<Pi address>:5000")
    print("(type  hostname -I  in another terminal to see the Pi address)")
    app.run(host="0.0.0.0", port=5000)

# TRY THIS:
#   1. Change the colours in STYLE (the #ffc93c is the button colour).
#   2. Add a "Party mode" button that blinks both lights 10 times.
#   3. Show "It's cold!" on the page when the temperature is under 18.
