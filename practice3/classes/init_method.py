"""All classes have a built-in method called __init__(), 
which is always executed when the class is being initiated.

The __init__() method is used to assign values to object properties, 
or to perform operations that are necessary when the object is being created."""

#!!! The __init__() method
#is called automatically every time the class is being used to create a new object.

#1
class Info:
  def __init__(self, name, age):
    self.name = name
    self.age = age

result = Info("Dayana", 18)

print(result.name)
print(result.age)

#2
class Info:
  def __init__(self, name, age=18):
    self.name = name
    self.age = age

e1 = Info("Dayana")
e2 = Info("Misa", 3)

print(e1.name, e1.age)
print(e2.name, e2.age)


#3
class Car:
    def __init__(self, brand, color, year):
        self.brand = brand
        self.color = color
        self.year = year

# Create cars
car1 = Car("Toyota", "red", 2020)
car2 = Car("Honda", "blue", 2022)
car3 = Car("Ford", "black", 2019)


print(f" - {car1.year} {car1.color} {car1.brand}")
print(f" - {car2.year} {car2.color} {car2.brand}")
print(f" - {car3.year} {car3.color} {car3.brand}")

#4
class Pet:
    def __init__(self, animal, name, age):
        self.animal = animal  
        self.name = name      
        self.age = age        

# Create pets
pet1 = Pet("dog", "Businka", 5)
pet2 = Pet("cat", "Misa", 2)
pet3 = Pet("fish", "Goldie", 1)


print(f" - {pet1.name} is a {pet1.animal}, age {pet1.age}")
print(f" - {pet2.name} is a {pet2.animal}, age {pet2.age}")
print(f" - {pet3.name} is a {pet3.animal}, age {pet3.age}")
