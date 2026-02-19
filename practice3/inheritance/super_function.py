# super() function that will make the child class inherit all the methods and properties from its parent
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        
    
    def introduce(self):
        return f"Hi, I'm {self.name}"

class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)  # Call parent __init__
        self.student_id = student_id
        
    
    def introduce(self):
        return f"{super().introduce()} and my ID is {self.student_id}"

s = Student("Dayana", 18, "25B032184")
print(s.introduce())

#2
class Vehicle:
    def __init__(self, brand, year):
        self.brand = brand
        self.year = year
    
    def info(self):
        return f"{self.year} {self.brand}"

class Car(Vehicle):
    def __init__(self, brand, year, doors):
        super().__init__(brand, year)
        self.doors = doors
    
    def info(self):
        return f"{super().info()} with {self.doors} doors"


car = Car("Toyota", 2022, 4)
print(car.info())

#3
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    
    def get_info(self):
        return f"{self.name} earns ${self.salary}"

class Manager(Employee):
    def __init__(self, name, salary, team_size):
        super().__init__(name, salary)
        self.team_size = team_size
    
    def get_info(self):
        return f"{super().get_info()}, manages {self.team_size} people"


mgr = Manager("Yan", 80000, 5)
print(mgr.get_info())

#4
class Food:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    def describe(self):
        return f"{self.name} costs ${self.price}"

class Pizza(Food):
    def __init__(self, name, price, size):
        super().__init__(name, price)
        self.size = size
   
    
    def describe(self):
        return f"{super().describe()} - {self.size}"

pizza = Pizza("Margherita", 12, "Large")
print(pizza.describe())
