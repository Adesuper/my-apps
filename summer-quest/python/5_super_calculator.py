# ==============================================
#  5. SUPER CALCULATOR   (Level-Up Challenge!)
#  YOU choose which operation to do.
#  New trick: if / elif to make a choice.
# ==============================================

print("=== Super Calculator ===")
print("You pick the operation:  +  -  *  /")

a  = int(input("First number:  "))
op = input("Which operation? (+ - * /)  ")
b  = int(input("Second number: "))

if op == "+":
    print(f"{a} + {b} = {a + b}")
elif op == "-":
    print(f"{a} - {b} = {a - b}")
elif op == "*":
    print(f"{a} * {b} = {a * b}")
elif op == "/":
    print(f"{a} / {b} = {a / b}")
else:
    print("Hmm, I don't know that one. Try  +  -  *  or  /")

print("Nice work, calculator boss!")

# TRY THIS:
#   - Add remainder: use  elif op == "%":  and print  a % b
