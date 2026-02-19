#the sorted() function can use a lambda as a key for custom sorting
#1
people = [("Dayana", 18), ("Liza", 19), ("Misa", 3)]
sorted_people = sorted(people, key=lambda x: x[1])
print(sorted_people)


#2
words = ["BMW","Porshe", "Mercedes"]
sorted_words = sorted(words, key=lambda x: len(x)) #Sort strings by length
print(sorted_words)

#3
words = ["apple", "pie", "banana", "cherry", "grape"]
sorted_by_first_char = sorted(words, key=lambda x: x[0]) #Sorted by first character
print(sorted_by_first_char)  


#4
words = ["apple", "pie", "banana", "cherry", "grape"]
sorted_by_last_char = sorted(words, key=lambda x: x[-1]) #Sorted by last character
print(sorted_by_last_char)  

