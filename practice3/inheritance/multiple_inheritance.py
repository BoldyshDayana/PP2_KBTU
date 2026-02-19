#1
class Flyer:
    def fly(self):
        return "I can fly!"

class Swimmer:
    def swim(self):
        return "I can swim!"

class Duck(Flyer, Swimmer):
    def quack(self):
        return "Quack quack!"

duck = Duck()
print(duck.fly())
print(duck.swim())
print(duck.quack())



#2
class Car:
    def drive(self):
        return "Driving on road"

class Airplane:
    def fly(self):
        return "Flying in air"

class FlyingCar(Car, Airplane):
    def transform(self):
        return "Transforming from car to plane!"

fc = FlyingCar()
print(fc.drive())
print(fc.fly())
print(fc.transform())



#3
class TV:
    def watch(self):
        return "Watching TV channels"

class Computer:
    def browse(self):
        return "Browsing internet"

class SmartTV(TV, Computer):
    def stream(self):
        return "Streaming Netflix!"

tv = SmartTV()
print(tv.watch())
print(tv.browse())
print(tv.stream())



#4
class LandVehicle:
    def drive(self):
        return "Moving on land"

class WaterVehicle:
    def sail(self):
        return "Moving on water"

class AmphibiousVehicle(LandVehicle, WaterVehicle):
    def __init__(self, name):
        self.name = name
    
    def transform(self):
        return f"{self.name} is transforming for water!"


amp = AmphibiousVehicle("Duck Boat")
print(amp.drive())
print(amp.sail())
print(amp.transform())
