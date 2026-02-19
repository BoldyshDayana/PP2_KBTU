#1
#A parameter is the variable listed inside the parentheses in the function definition.
#An argument is the actual value that is sent to the function when it is called.

def my_function(name): #name is a parameter
  print("Hello", name)

my_function("Dayana") #"Dayana" is an argument


#2
#If your function expects 4 arguments, you must call it with exactly 4 arguments.
def display_person_info(first_name, last_name, age, city):
    print(f"Name: {first_name} {last_name}")
    print(f"Age: {age}")
    print(f"City: {city}")
# Calling the function
display_person_info("Dayana", "Boldysh", 18, "Amaty")



#3
def myFunction(name = "anonymous"):
  print("Hello", name)

myFunction("Dayana")
myFunction("Misa")
myFunction() #If the function is called without an argument, it uses the default value


#4
#Mixing Positional and Keyword Arguments
def display_pet_info(animal, name, age, color="unknown"):
    print(f"Pet Type: {animal}")
    print(f"Name: {name}")
    print(f"Age: {age} years old")
    print(f"Color: {color}")


display_pet_info("dog", name="Buddy", age=5)  # Uses default color
display_pet_info("parrot", name="Rio", age=2, color="blue")

#5
#Without the , / you are actually allowed to use keyword arguments
#With , /, you will get an error if you try to use keyword arguments:
def myFunction(name, /): #To specify positional-only arguments
  print("Hello", name)

myFunction("Dayana")

#To specify that a function can have only keyword arguments, add *
#With *, you will get an error if you try to use positional arguments:
def myFunction(*, name):
  print("Hello", name)

myFunction(name = "Liza")