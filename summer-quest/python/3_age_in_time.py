# ==============================================
#  3. HOW OLD ARE YOU... REALLY?
#  See your age in days, hours, minutes AND seconds!
# ==============================================

print("=== Age-in-Time Machine ===")
age = int(input("How many years old are you? "))

days    = age * 365
hours   = days * 24
minutes = hours * 60
seconds = minutes * 60

print("\nWhoa! Here is your age measured different ways:")
print(f"About {days} days old")
print(f"About {hours} hours old")
print(f"About {minutes} minutes old")
print(f"About {seconds} seconds old!")
print("\nThat is a LOT of seconds -- and your heart beat through every one.")

# TRY THIS:
#   - Add: heartbeats = minutes * 80   (about 80 beats a minute!)
#     then print how many times your heart has beaten.
