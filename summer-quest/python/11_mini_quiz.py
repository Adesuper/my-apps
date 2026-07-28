# ==============================================
#  11. MINI QUIZ
#  Put it all together: input + if / else + keeping a score.
# ==============================================

score = 0

ans1 = input("Question 1:  What is 7 x 8?  ")
if ans1 == "56":
    print("Correct!")
    score = score + 1
else:
    print("The answer is 56.")

ans2 = input("Question 2:  Is 12 even or odd?  ")
if ans2 == "even":
    print("Correct!")
    score = score + 1
else:
    print("12 is even.")

print("You scored " + str(score) + " out of 2.")

# TRY THIS:
#   - Add a third question of your own and add 1 to score if it is right.
