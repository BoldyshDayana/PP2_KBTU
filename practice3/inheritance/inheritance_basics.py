"""Inheritance allows us to define a class that inherits all the methods 
and properties from another class.

Parent class is the class being inherited from, also called base class.

Child class is the class that inherits from another class, also called derived class."""

#1
#Parent class(Base class)
class Animal:
    def __init__(self, name):
        self.name = name
        self.alive = True
    
    def eat(self):
        return f"{self.name} is eating"
    
    def sleep(self):
        return f"{self.name} is sleeping"

#Child class(Derived class)-inherits from Animal
class Dog(Animal):
    def bark(self):
        return f"{self.name} says Woof!"

#Child class-inherits from Animal
class Cat(Animal):
    def meow(self):
        return f"{self.name} says Meow!"

#Create examples
dog = Dog("Businka")
cat = Cat("Umka")

print(dog.eat())      # From parent
print(dog.sleep())    # From parent
print(dog.bark())     # From child

print(cat.eat())      # From parent
print(cat.sleep())    # From parent
print(cat.meow())     # From child


#2
class Vehicle:
    def __init__(self, brand):
        self.brand = brand
    
    def start(self):
        return f"{self.brand} is starting"

class Car(Vehicle):
    def drive(self):
        return f"{self.brand} car is driving"

class Motorcycle(Vehicle):
    def wheelie(self):
        return f"{self.brand} motorcycle doing wheelie"


car = Car("Toyota")
bike = Motorcycle("Harley")
print(car.start())
print(car.drive())
print(bike.start())
print(bike.wheelie())




#3
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    
    def work(self):
        return f"{self.name} is working"

class Manager(Employee):
    def manage(self):
        return f"{self.name} is managing team"

class Developer(Employee):
    def code(self):
        return f"{self.name} is coding"

mgr = Manager("Alice", 80000)
dev = Developer("Yan", 70000)
print(mgr.work())
print(mgr.manage())
print(dev.work())
print(dev.code())


#4
class Device:
    def __init__(self, brand):
        self.brand = brand
        self.power = False
    
    def turn_on(self):
        self.power = True
        return f"{self.brand} device turned on"

class Phone(Device):
    def call(self, number):
        if self.power:
            return f"Calling {number}"
        return "Phone is off"

class Laptop(Device):
    def code(self):
        if self.power:
            return f"Coding on {self.brand} laptop"
        return "Laptop is off"


phone = Phone("iPhone")
laptop = Laptop("HP")
print(phone.turn_on())
print(phone.call("1234567"))
print(laptop.turn_on())
print(laptop.code())
