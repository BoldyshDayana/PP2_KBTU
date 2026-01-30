#1
i = 1
while i < 5:
  print(i)
  if i == 3:
    break
  i += 1

#2
money = 1
while True:  
    print(f"I have ${money}")
    
    if money >= 100:
        print("I'm rich!")
        break
    
    money = money * 2

#3
count = 1
while count <= 20:
    print(count)
    if count == 10:
        break
    count += 1

#4
score = 0
while True:
    score += 5
    print(f"Score: {score}")
    
    if score >= 15:
        print("You win!")
        break

#5
i = 1
while i < 10:
  print(i)
  if i == 5:
    break
  i += 1