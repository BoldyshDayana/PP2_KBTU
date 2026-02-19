"""Python is an object oriented programming language.
Almost everything in Python is an object, with its properties and methods.
A Class is like an object constructor, or a "blueprint" for creating objects."""

#1
class MyClass:
    x = 10  # Class attribute 

# Create first instance
example1 = MyClass()
print("example1.x =", example1.x)  

#2
# Delete the instance
del example1  # p1 no longer exists

#3
# Create new instances
example1 = MyClass()  # Create a new example1
example2 = MyClass()
example3 = MyClass()

#4
print("example1.x =", example1.x)  
print("example2.x =", example2.x)      
print("example3.x =", example3.x)      

#5
class My_class:
  pass #Empty class - does nothing yet