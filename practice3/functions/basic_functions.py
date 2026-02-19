#1
#This function just prints a message
def hello_world():
    print("Hello, World!") #printing

#Calling the function
hello_world()



#2
#This function takes a Fahrenheit temperature, converts it to Celsius, and returns the result
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit-32)*5/9 #sends the result back to where the function was called

#Testing
print(fahrenheit_to_celsius(32))   
print(fahrenheit_to_celsius(212))   
print(fahrenheit_to_celsius(98.6)) 
print(fahrenheit_to_celsius(-40))  

#3
#This function takes a name and creates a personalized greeting
def greeting(name):
    return f"Hello, {name}!"

#Storing the returned value in a variable
message = greeting("Dayana")
print(message)
print(greeting("Liza"))



#4
# The 'pass' statement is used when you need a function but don't want to write the code yet
# This prevents errors from an empty function
def test():
  pass




#5
#This function checks if a number is even by seeing if it's divisible by 2
def is_even(number):
    return number % 2 == 0

# Test different numbers
numbers = [2, 7, 10, 15, 22, 33]

for num in numbers:
    if is_even(num):
        print(f"{num} is even")
    else:
        print(f"{num} is odd")