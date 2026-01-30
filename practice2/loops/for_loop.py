#1
animals = ["lion", "tiger", "capibara"]
for animal in animals:
  print(animal)

#2
for x in "KBTU":
  print(x)

#3
for x in range(4):
  print(x)

#4
for x in range(1,4):
  print(x)

#5
for x in range(1, 10, 2):
  print(x)

#6
countries = ["USA", "Japan", "Germany"]
foods = ["burger", "sushi", "sausage"]

for country in countries:
    for food in foods:
        print(f"In {country}, try {food}!")