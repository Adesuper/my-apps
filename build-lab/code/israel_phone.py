# ==================================================================
#  LEVEL 3  --  THE ISRAEL PHONE (home screen with my own apps)
#  For a Raspberry Pi with the Touch Display 2 and Camera Module 3.
#  Every app is a Python function. Add your own apps at the bottom!
#
#  Run it:   python3 israel_phone.py
#  Quit:     the red  X  button on the home screen
#  Photos are saved in the  Pictures  folder.
# ==================================================================

import os
import random
import shutil
import subprocess
import time
import tkinter as tk
import webbrowser

OWNER = "Israel"                       # <-- your name on the home screen
SMART_ROOM = "http://localhost:5000"   # the Smart Room page from level 1
PHOTOS = os.path.expanduser("~/Pictures")

root = tk.Tk()
root.title(OWNER + " Phone")
root.attributes("-fullscreen", True)
root.configure(bg="#101735")
BIG = ("DejaVu Sans", 22, "bold")
HUGE = ("DejaVu Sans", 34, "bold")
screen = tk.Frame(root, bg="#101735")
screen.pack(fill="both", expand=True)


def clear():
    for child in screen.winfo_children():
        child.destroy()


def button(parent, text, command, colour="#ffc93c"):
    return tk.Button(parent, text=text, command=command, font=BIG, bg=colour,
                     fg="#101735", activebackground="#ffe27a", bd=0,
                     padx=10, pady=18, wraplength=260)


def back_button():
    button(screen, "< Home", home, "#8fa8ff").pack(side="bottom", fill="x", padx=12, pady=12)


# ------------------------------------------------------------------ apps
def camera_app():
    clear()
    tk.Label(screen, text="Camera", font=HUGE, bg="#101735", fg="white").pack(pady=10)
    status = tk.Label(screen, text="Smile! Press the button.", font=BIG, bg="#101735", fg="white")
    status.pack(pady=10)
    picture = tk.Label(screen, bg="#101735")
    picture.pack(pady=10)

    def snap():
        os.makedirs(PHOTOS, exist_ok=True)
        path = os.path.join(PHOTOS, "photo_" + time.strftime("%Y%m%d_%H%M%S") + ".png")
        tool = shutil.which("rpicam-still") or shutil.which("libcamera-still")
        if not tool:
            status.config(text="Camera program not found.")
            return
        status.config(text="3... 2... 1...")
        root.update()
        subprocess.run([tool, "-t", "2000", "-e", "png", "--width", "640",
                        "--height", "480", "-o", path])
        if os.path.exists(path):
            img = tk.PhotoImage(file=path).subsample(2)
            picture.config(image=img)
            picture.image = img          # keep a reference so it stays visible
            status.config(text="Saved in Pictures!")
        else:
            status.config(text="No photo. Is the camera cable in?")

    button(screen, "Take a photo", snap).pack(pady=10)
    back_button()


def calculator_app():
    clear()
    shown = tk.StringVar(value="")
    tk.Label(screen, textvariable=shown, font=HUGE, bg="white", fg="#101735",
             anchor="e", padx=12).pack(fill="x", padx=12, pady=12)
    pad = tk.Frame(screen, bg="#101735")
    pad.pack(expand=True)
    keys = ["7", "8", "9", "/", "4", "5", "6", "*", "1", "2", "3", "-", "C", "0", "=", "+"]

    def press(k):
        if k == "C":
            shown.set("")
        elif k == "=":
            text = shown.get()
            if text and all(ch in "0123456789+-*/. " for ch in text):
                try:
                    result = eval(text)        # safe: only digits and + - * / allowed
                    shown.set(str(round(result, 4)))
                except (ZeroDivisionError, SyntaxError):
                    shown.set("Oops!")
        else:
            if shown.get() == "Oops!":
                shown.set("")
            shown.set(shown.get() + k)

    for i, k in enumerate(keys):
        tk.Button(pad, text=k, font=HUGE, width=3, bg="#24318a", fg="white", bd=0,
                  command=lambda k=k: press(k)).grid(row=i // 4, column=i % 4, padx=4, pady=4)
    back_button()


def quiz_app():
    clear()
    score = {"right": 0, "asked": 0}
    question = tk.Label(screen, font=HUGE, bg="#101735", fg="white")
    question.pack(pady=20)
    answer = tk.Entry(screen, font=HUGE, width=6, justify="center")
    answer.pack(pady=10)
    result = tk.Label(screen, font=BIG, bg="#101735", fg="#ffe27a")
    result.pack(pady=10)
    numbers = {}

    def new_question():
        numbers["a"], numbers["b"] = random.randint(2, 12), random.randint(2, 12)
        question.config(text="%d x %d = ?" % (numbers["a"], numbers["b"]))
        answer.delete(0, "end")

    def check():
        score["asked"] += 1
        good = numbers["a"] * numbers["b"]
        if answer.get().strip() == str(good):
            score["right"] += 1
            result.config(text="Bravo!  Score: %d / %d" % (score["right"], score["asked"]))
        else:
            result.config(text="It was %d.  Score: %d / %d" % (good, score["right"], score["asked"]))
        new_question()

    button(screen, "Check", check).pack(pady=10)
    new_question()
    back_button()


def flashlight_app():
    clear()
    light = tk.Button(screen, text="Tap to turn off", font=BIG, bg="white", fg="#888888",
                      bd=0, command=home)
    light.pack(fill="both", expand=True)


def smart_room_app():
    webbrowser.open(SMART_ROOM)


# ------------------------------------------------------------- home screen
APPS = [
    ("Camera", camera_app),
    ("Calculator", calculator_app),
    ("Times tables", quiz_app),
    ("Flashlight", flashlight_app),
    ("Smart Room", smart_room_app),
]


def home():
    clear()
    tk.Label(screen, text=OWNER + " Phone", font=HUGE, bg="#101735", fg="white").pack(pady=(16, 2))
    tk.Label(screen, text=time.strftime("%H:%M"), font=BIG, bg="#101735", fg="#ffe27a").pack()
    grid = tk.Frame(screen, bg="#101735")
    grid.pack(expand=True, fill="both", padx=12, pady=12)
    for i, (name, app) in enumerate(APPS):
        button(grid, name, app).grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
    for c in range(2):
        grid.columnconfigure(c, weight=1)
    button(screen, "X", root.destroy, "#ee7d8b").pack(side="bottom", pady=8)


home()
root.mainloop()

# TRY THIS (your own apps!):
#   1. A "Dice" app: a big button that shows a random number from 1 to 6.
#   2. A "Secret code" app like the Secret Door from the summer.
#   3. Add your app to the APPS list so it appears on the home screen.
