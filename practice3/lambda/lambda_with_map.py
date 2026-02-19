#The map() function applies a function to every item in an iterable
#1
numbers = [1, 2, 3]
result = list(map(lambda x: x * 2, numbers))
print(result)

#2
words = ["apple", "banana", "cherry"]
word_lengths = list(map(lambda word: len(word), words))
print("Words:", words)
print("Lengths:", word_lengths)  


#3
fruits = ["apple", "banana", "cherry"]
uppercase_fruits = list(map(lambda fruit: fruit.upper(), fruits))
print("Uppercase:", uppercase_fruits) 


#4
words = ["Python", "Java", "JavaScript", "C++"]
first_letters = list(map(lambda word: word[0], words))
print("First letters:", first_letters)  

