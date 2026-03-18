
"""Use enumerate() and zip() for paired iteration
Demonstrate type checking and conversions
"""

#1
shopping = ["bread", "milk", "eggs", "cheese"]
prices = [2.5, 3.0, 4.5, 6.0]

print("Shopping list:")
for i, (item, price) in enumerate(zip(shopping, prices), 1):
    print(f"  {i}. {item:10} - ${price:.2f}")



students = ["Diana", "Dayana", "Alina"]
ages = [27, 18, 14]
grades = ["B", "A", "C"]

print("Student information:")
for student, age, grade in zip(students, ages, grades):
    print(f"  {student}: {age} years old, grade {grade}")



#2
print("\n1. Checking data types:")
for item in shopping:
    print(f"  '{item}' is {type(item).__name__}")
for price in prices:
    print(f"  {price} is {type(price).__name__}")

# Convert string to number
print("\n2. String to number conversion:")
user_input = "25.50"  # simulating user input
if isinstance(user_input, str):
    print(f"  User input: '{user_input}' (type: {type(user_input).__name__})")
    number = float(user_input)
    print(f"  Converted to: {number} (type: {type(number).__name__})")
