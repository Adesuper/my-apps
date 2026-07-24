# ==============================================
#  4. PIZZA PARTY DIVIDER
#  Share slices fairly and see the leftovers.
#  This is the SAME division + remainder you do in math!
#    //  gives the whole number each person gets
#    %   gives the leftover (the remainder)
# ==============================================

print("=== Pizza Party Divider ===")
slices  = int(input("How many pizza slices are there? "))
friends = int(input("How many friends are sharing? "))

each     = slices // friends   # whole slices per friend
leftover = slices %  friends   # slices left over

print(f"\nEach friend gets {each} slices.")
print(f"There are {leftover} slices left over.")

if leftover == 0:
    print("Perfect sharing -- nothing left!")
else:
    print("Someone gets seconds! Who will it be?")

# TRY THIS:
#   - Change it to share candies, or stickers, instead of pizza.
#   - Try 13 slices and 4 friends. What is the remainder?
