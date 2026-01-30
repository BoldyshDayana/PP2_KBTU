#1
cars = ["BMW", "Mercedes", "Porsche"]
for car in cars:
  print(car)
  if car == "Porsche":
    break

#2
colors = ["red", "purple", "pink"]
for x in colors:
  if x == "pink":
    break
  print(x)

#3
names = ["Anthony", "Benedict", "Colin", "Daphne", "Eloise", "Francesca", "Gregory", "Hyacinth"]
search_name = "Eloise"

for name in names:
    print(f"Checking: {name}")
    if name == search_name:
        print(f"Found {search_name}!")
        break
print("Search completed")

#4
numbers = [1, 3, 5, 8, 9, 10, 12]

for num in numbers:
    if num % 2 == 0:
        print(f"First even number: {num}")
        break

#5
for i in range(1, 10):
    print(f"Try {i}")
    if i == 3:
       break