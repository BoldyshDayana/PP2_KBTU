#1
class Animal:
    def make_sound(self):
        return "Some sound"

class Dog(Animal):
    def make_sound(self):  #Override
        return "Woof! Woof!"

class Cat(Animal):
    def make_sound(self):  #Override
        return "Meow!"

class Cow(Animal):
    def make_sound(self):  #Override
        return "Moo!"


animals = [Dog(), Cat(), Cow()]
for animal in animals:
    print(f"{animal.__class__.__name__}: {animal.make_sound()}")


#2
class Greeting:
    def say_hello(self):
        return "Hello"

class English(Greeting):
    def say_hello(self):
        return "Hello!"

class Spanish(Greeting):
    def say_hello(self):
        return "¡Hola!"

class French(Greeting):
    def say_hello(self):
        return "Bonjour!"


greetings = [English(), Spanish(), French()]
for g in greetings:
    print(g.say_hello())


#3
class Vehicle:
    def move(self):
        return "Moving"

class Car(Vehicle):
    def move(self):
        return "Driving on road"

class Boat(Vehicle):
    def move(self):
        return "Sailing on water"

class Airplane(Vehicle):
    def move(self):
        return "Flying in sky"

vehicles = [Car(), Boat(), Airplane()]
for v in vehicles:
    print(v.move())

#4
class Notification:
    def send(self, message):
        return f"Sending: {message}"

class Email(Notification):
    def send(self, message):
        return f"Email: {message}"

class SMS(Notification):
    def send(self, message):
        return f"SMS: {message}"

class Push(Notification):
    def send(self, message):
        return f"Push notification: {message}"

notifications = [Email(), SMS(), Push()]
for note in notifications:
    print(note.send("Hello World"))

