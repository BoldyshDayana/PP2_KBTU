#Data stored inside an object (like nouns/adjectives)
#Attributes/Variables


#1
class Person:
    def __init__(self, name, age):
        self.name = name    #property
        self.age = age      #property

#Using properties
p = Person("Dayana", 18)
print(p.name)  #Getting property value
p.age = 19   #Setting property value
print(p.age)




#2
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

e1 = Person("Misa", 3)
print(e1.name, e1.age)

e1.age = 4 #Modify Properties
print(e1.name, e1.age)


#3
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

e1 = Person("Liza", 19)
del e1.age #Delete Properties
print(e1.name) 

#4
class Car:
    wheels = 4  #Class property-all cars have 4 wheels
    
    def __init__(self, color):
        self.color = color  #Instance property- ach car can have different color

car1 = Car("red")
car2 = Car("blue")

print(f"Car 1: {car1.color}, {car1.wheels} wheels")
print(f"Car 2: {car2.color}, {car2.wheels} wheels")

