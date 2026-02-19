#*args and **kwargs allow functions to accept a unknown number of arguments.

#1
#Arbitrary Arguments - *args
def show_all_children(*children): #*args - Accept any number of arguments
    print("All children:")
    for child in children:
        print(f"-{child}")

show_all_children("Dayana", "Diana", "Alina")


#2
def myFunction(greeting, *names):
  for name in names:
    print(greeting, name)

myFunction("Hello", "Diana", "Dayana", "Alina")

#3
def myFunction(*numbers):
  total = 0
  for num in numbers:
    total += num
  return total

print(myFunction(1, 2, 3))
print(myFunction(24, 7 , 7 , 18))
print(myFunction(100))


#Arbitrary Keyword Arguments - **kwargs
#4
def person_info(**info): #**kwargs - Accept any number of keyword arguments
    for key, value in info.items(): 
        print(f"{key}: {value}")

person_info(name="Dayana", age=18, city="Almaty")

#5
def myFunction(title, *args, **kwargs):
  print("Title:", title)
  print("Positional arguments:", args)
  print("Keyword arguments:", kwargs)

myFunction("User Info", "Dayana", "Boldysh", age = 18, city = "Almaty")
# Use * and ** in function definitions to collect arguments
#and use them in function calls to unpack arguments