# ==============================================
#  8. EVEN OR ODD   (this is your MATH class, in code!)
#  % gives the remainder. If a number divided by 2 leaves 0, it is even.
# ==============================================

num = int(input("Type a whole number: "))

if num % 2 == 0:
    print(str(num) + " is EVEN.")
else:
    print(str(num) + " is ODD.")

# TRY THIS:
#   - Try 10, 7, 24 and 51.
#   - Change 2 to 5 and % to test "counts by 5" (num % 5 == 0).
