# ==============================================
#  1. HELLO CALCULATOR
#  This is the program you built in class today!
#  It asks for two numbers, then does the math.
# ==============================================

print("Welcome to my calculator!")
print("-----------------------------")

# IMPORTANT: input() always gives us TEXT (letters), even when you type digits.
# To do math we must turn that text into a NUMBER using int(...).
first  = int(input("Type your first number:  "))
second = int(input("Type your second number: "))

# Now we can do arithmetic and print each answer.
print("Add:      ", first, "+", second, "=", first + second)
print("Subtract: ", first, "-", second, "=", first - second)
print("Multiply: ", first, "*", second, "=", first * second)
print("Divide:   ", first, "/", second, "=", first / second)

print("Ta-da! You did four calculations at once.")

# TRY THIS:
#   - Add a line that shows first + second + 10
#   - Change the welcome message to your own name
