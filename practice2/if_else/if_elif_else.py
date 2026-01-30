#1
num1 = 31231
num2 = 939
if num2 > num1:
  print("num2 > num1")
elif num1 == num2:
  print("num1 == num2")
else:
  print("num2 < num1")

#2
temp = int(input("temperature:"))
if temp > 30:
  print("HOT")
elif temp > 20:
  print("WARM")
elif temp > 10:
  print("NICE")
else:
  print("COLD")

#3
num1 = 5
num2 = 5
if num1 > num2:
  print("num1 > num2")
elif num1 == num2:
  print("num1 == num2")
else:
  print("num1 < num2")

#4
age = int(input("Age:"))
if age < 13:
  print("child")
elif age < 20:
  print("teenager")
elif age < 65:
  print("adult")
elif age >= 65:
  print("senior")

#5
day = int(input("day:"))
if day == 1 or day == 2 or day == 3 or day == 4 or day == 5:
  print("You need to work!")
elif day==6 or day ==7:
  print("The weekend!")
else:
  print("error")