#1
"""Create a generator that generates the squares of numbers up to some number N."""
def task1():
    def squares_generator(N):
        for i in range(1, N+1):
            yield i*i
    N = int(input("N = "))
    for x in squares_generator(N):
        print(x)

#2
"""Write a program using generator to print the even numbers between 0 and n 
in comma separated form where n is input from console."""

def task2():
    def even_generator(N):
        for i in range(0, N+1, 2):
            yield i
    N = int(input("N = "))
    print(",".join(map(str, even_generator(N))))



#3
"""Define a function with a generator which can iterate the numbers,
which are divisible by 3 and 4, between a given range 0 and n."""
def task3():
    def divisible_by_3_and_4(N):
        for i in range(0, N+1):
            if i%3==0 and i%4==0:
                yield i
    N = int(input("N = "))
    for x in divisible_by_3_and_4(N):
        print(x)

#4
"""Implement a generator called squares to yield the square of all numbers from (a) to (b).
 Test it with a "for" loop and print each of the yielded values."""

def task4():
    def squares(a, b):
        for i in range(a, b+1):
            yield i*i
    a, b = map(int, input("a, b = ").split())
    for x in squares(a, b):
        print(x)

#5
"""Implement a generator that returns all numbers from (n) down to 0."""

def task5():
    def countdown(N):
        for i in range(N, -1, -1):
            yield i
    N = int(input("N = "))
    for x in countdown(N):
        print(x)

#menu
while True:
    c = input("Choose the number of task:")
    if c == "1": task1()
    elif c == "2": task2()
    elif c == "3": task3()
    elif c == "4": task4()
    elif c == "5": task5()
    elif c == "0": break
    else: print("Error")