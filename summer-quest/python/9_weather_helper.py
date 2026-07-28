# ==============================================
#  9. WEATHER HELPER
#  New trick: elif lets you check MORE than two choices.
# ==============================================

weather = input("How is the weather? (sunny / rainy / snowy) ")

if weather == "sunny":
    print("Wear your sunglasses and a hat!")
elif weather == "rainy":
    print("Take an umbrella and your boots.")
elif weather == "snowy":
    print("Put on a warm coat and gloves.")
else:
    print("Hmm, I do not know that weather.")

# TRY THIS:
#   - Add an elif for "windy".
#   - Careful: "Sunny" is not the same as "sunny" (capitals matter!).
