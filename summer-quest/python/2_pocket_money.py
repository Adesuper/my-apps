# ==============================================
#  2. POCKET MONEY PLANNER
#  How many weeks until you can buy what you want?
#  New trick: f-strings -- put values right inside a sentence!
# ==============================================

print("=== Pocket Money Planner ===")

thing     = input("What do you want to buy? ")
price     = int(input(f"How much does {thing} cost?  $"))
allowance = int(input("How much pocket money do you get each week?  $"))

weeks = price / allowance

# An f-string starts with f"..." and lets you drop values inside { }.
print(f"\n{thing} costs ${price}.")
print(f"You save ${allowance} every week.")
print(f"So you need about {weeks} weeks to buy it.")
print("Save a little extra and you'll get there even faster!")

# TRY THIS:
#   - What if you saved DOUBLE each week? (allowance * 2)
#   - Add a birthday gift of $20: change price to price - 20
