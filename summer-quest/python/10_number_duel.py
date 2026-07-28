# ==============================================
#  10. NUMBER DUEL
#  Ask for two numbers and let if / elif / else find the bigger one.
# ==============================================

a = int(input("First number:  "))
b = int(input("Second number: "))

if a > b:
    print(str(a) + " is bigger.")
elif a < b:
    print(str(b) + " is bigger.")
else:
    print("They are equal!")

# TRY THIS:
#   - Add a line that also prints their total: a + b.
