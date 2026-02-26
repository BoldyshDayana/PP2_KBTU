#1
"""Write a Python program to convert degree to radian."""
import math

degree=int(input())
radian=math.radians(degree)
print(f"Input degree: {degree}")
print(f"Output radian: {radian}")
print("-"*50)

#2
"""Write a Python program 
to calculate the area of a trapezoid."""
height = int(input())
base1 = int(input())
base2 = int(input())
area = ((base1 + base2) / 2) * height
print(f"Height: {height}")
print(f"Base, first value: {base1}")
print(f"Base, second value: {base2}")
print(f"Expected Output: {area}")
print("-"*50)

#3
"""Write a Python program 
to calculate the area of regular polygon."""

n = int(input("Input number of sides: "))
s = float(input("Input the length of a side: "))
area = (n * s**2) / (4 * math.tan(math.pi / n))
print(f"The area of the polygon is {int(area)}")
print("-"*50)

#4
"""Write a Python program 
to calculate the area of a parallelogram."""

l = int(input("Input length of base: "))
h = int(input("Input length of height: "))
area = float(l*h)
print(f"Length of base: {l}")
print(f"Height of parallelogram: {h}")
print(f"Area of parallelogram: {area}")