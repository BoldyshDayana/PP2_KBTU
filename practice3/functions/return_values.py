#1
def myFunction(x, y):
  return x * y #Returns the product of x and y

answer = myFunction(6, 7)
print(answer)

#2
def get_colors():
    return ["red", "blue", "yellow"] #Returns a list with 3 items

colors = get_colors()
print(colors[0])  
print(colors[1])   
print(colors[2])  


#3
def get_coordinates():
    return (5, 10)   #Returns a tuple with two values 

x, y = get_coordinates()
print(f"x: {x}")
print(f"y: {y}")

#4
def add_numbers(x, y, /, *, z):
    return x + y + z

result = add_numbers(5, 10, z=15) 
print(f"5 + 10 + 15 = {result}")
# add_numbers(5, 10, 15)     #ERROR! z must be named
# add_numbers(x=5, y=10, z=15) #ERROR! x,y can't be named

