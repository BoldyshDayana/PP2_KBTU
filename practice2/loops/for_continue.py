#1
drinks = ["tea", "juice", "water"]
for x in drinks:
  if x == "juice":
    continue
  print(x)

#2
numbers = [1, 2, 3, 4, 5, 6]
for num in numbers:
    if num % 2 == 0:  
        continue
    print(num)

#3
weather = ["sunny", "rainy", "cloudy", "stormy", "sunny"]
for day in weather:
    if day == "stormy":
        continue 
    print(f"Go outside: {day}")

#4
fruits = ["mango", "blueberry", "cherry", "strawberry"]
for fruit in fruits:
    if fruit == "mango":
        continue  
    print(f"I like {fruit}")

#5
hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
for hour in hours:
    if hour == 13:  
        continue
    print(f"{hour}:00 - Working")