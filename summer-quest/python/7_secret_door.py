# ==============================================
#  7. SECRET DOOR
#  A password checker. == asks "are these the same?"
# ==============================================

print("=== Secret Door ===")
code = input("Enter the secret word: ")

if code == "dragon":
    print("Correct! The door opens. Welcome in!")
else:
    print("Wrong word. The door stays shut.")

# TRY THIS:
#   - Change the secret word to your own.
#   - Add an elif for a second word like "phoenix".
