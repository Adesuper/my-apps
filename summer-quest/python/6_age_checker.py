# ==============================================
#  6. AGE CHECKER
#  Ask for info, then let if / else decide what to say.
# ==============================================

name = input("What is your name? ")
age  = int(input("How old are you? "))   # int(...) turns the text into a number

if age >= 8:
    print("Wow " + name + ", you are a big kid!")
else:
    print("Hi " + name + ", you are a little star!")

# TRY THIS:
#   - Change 8 to your own age.
#   - Add an elif for age >= 13 that prints "You are a teenager!"
