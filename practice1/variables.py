x = 5
y = "John"
print(x)
print(y)

x = 4       #int
x = "Sally" #str
print(x)


x = str(3)    #3
y = int(3)    #3
z = float(3)  #3.0

#get the type
x = 5
y = "John"
print(type(x))
print(type(y))

x = "John"
#is the same as
x = 'John'

a = 4
A = "Sally"
#A will not overwrite a


#Legal variable names:
myvar = "John"
my_var = "John"
_my_var = "John"
myVar = "John"
MYVAR = "John"
myvar2 = "John"

#Multi Words Variable Names
myVariableName = "John" #camel case
MyVariableName = "John" #pascal case
my_variable_name = "John" #snake case

#Assign Multiple Values
x, y, z = "Orange", "Banana", "Cherry"
print(x)
print(y)
print(z)

x = y = z = "Orange"
print(x)
print(y)
print(z)

fruits = ["apple", "banana", "cherry"]
x, y, z = fruits
print(x)
print(y)
print(z)

x = "Python is awesome"
print(x)

x = "Python"
y = "is"
z = "awesome"
print(x, y, z)
print(x + y + z)

#Global Variables
x = "awesome"

def myfunc():
  print("Python is " + x)

myfunc()


x = "awesome"

def myfunc():
  x = "fantastic"
  print("Python is " + x)

myfunc()

print("Python is " + x)