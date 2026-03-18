"""Use map() and filter() on lists
Aggregate with reduce() (from functools)"""

from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

squared = list(map(lambda x: x**2, numbers))

evens = list(filter(lambda x: x%2==0, numbers))

print(f"Squared numbers: {squared}\nEven numbers: {evens}")

product = reduce(lambda x, y: x*y, numbers)
print(f"Product of numbers is {product}")