#The filter() function creates a list of items for which a function returns True
#1
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", even_numbers)  

#2
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
greater_than_5 = list(filter(lambda x: x > 5, numbers))
print("Numbers greater than 5:", greater_than_5)  

#3
words = ["apple", "banana", "avocado", "cherry","grape"]
a_words = list(filter(lambda word: word.startswith('a'), words))
print("Words starting with 'a':", a_words)  

#4
numbers = [-5, 3, -2, 7, 0, -1, 8, -4]
positive = list(filter(lambda x: x > 0, numbers))
print("Positive numbers:", positive)  
