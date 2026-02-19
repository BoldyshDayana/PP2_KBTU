#A lambda function is a small anonymous function.
#A lambda function can take any number of arguments,but can only have one expression

#1
#Add 24 to argument a, and return the result
x = lambda a : a + 24
print(x(7))


#2
x = lambda a, b, c : a + b + c
print(x(24, 7, 7))


#3
def myFunction(n):
  return lambda a : a * n

answer=myFunction(5)
print(answer(2))

#4
def create_greeting(prefix):
    return lambda name: f"{prefix}, {name}!"

hello = create_greeting("Hello")
hi = create_greeting("Hi")
goodbye = create_greeting("Goodbye")

print(hello("Dayana"))
print(hi("Liza"))
print(goodbye("Misa"))

#Use lambda functions when an anonymous function is required for a short period of time.