#1
num1 = 24
num2 = 7
if num1 > num2: print("num1 > num2")


#2
num3 = 2026
num4 = 2025
print(2026) if num3 > num4 else print(2025)

#3
n1 = 24
n2 = 24
print("n1 > n2") if n1 > n2 else print("n1 > n2") if n1 == n2 else print("n1 == n2")

#4
num1 = int(input("number1:"))
num2 = int(input("number2:"))
max_num = num1 if num1 > num2 else num2
print("Maximum:", max_num)

#5
name = input("Name:")
display = name if name else "guest"
print("Welcome,", display)