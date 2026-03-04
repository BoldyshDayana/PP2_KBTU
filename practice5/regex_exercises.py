import re

#1
"""Write a Python program that matches a string that has an 'a' followed by zero or more 'b''s."""
def Task1(text):
    x=re.findall("^ab*$", text)
    if x:
        return "Match is found"
    else:
        return "Doesn't match"

print("Task1")
print(f"ab: {Task1('ab')}")
print(f"abb: {Task1('abb')}")
print(f"a: {Task1('a')}")
print(f"b: {Task1('b')}")
print(f"abc: {Task1('abc')}")
print("-"*50)

#2
"""Write a Python program that matches a string that has an 'a' followed by two to three 'b'."""
def Task2(text):
    pattern = r"^ab{2,3}$"
    if re.search(pattern, text):
        return "Match is found"
    else:
        return "Doesn't match"


print("Task2")
print(f"ab: {Task2('ab')}")
print(f"abb: {Task2('abb')}")
print(f"a: {Task2('a')}")
print(f"abc: {Task2('abc')}")
print("-"*50)

#3
"""Write a Python program to find sequences of lowercase letters joined with a underscore."""
def Task3(text):
    result=re.findall("[a-z]+_[a-z]", text)
    if result:
        return f"Found: {result}"
    else:
        return "Didn't found"

print("Task3")
print(Task3('ab'))
print(Task3('a_b'))
print("-"*50)


#4
"""Write a Python program to find the sequences
 of one upper case letter followed by lower case letters."""

def Task4(text):
    result=re.findall("^[A-Z][a-z]", text)
    if result:
        return f"Found: {result}"
    else:
        return "Didn't found"

print("Task4")
print(Task4('ab'))
print(Task4('AB'))
print(Task4('Ab'))
print("-"*50)

#5
"""Write a Python program that matches a string 
that has an 'a' followed by anything, ending in 'b'."""
def Task5(text):
    x=re.search("^a.*b$", text)
    if x:
        return "Match is found"
    else:
        return "Doesn't match"

print("Task5")
print(Task5('ab'))
print(Task5('abc'))
print(Task5('accb'))
print("-"*50)

#6
"""Write a Python program to replace all occurrences of space, comma, or dot with a colon."""
def Task6(text):
    pattern=r"[,.]"
    x=re.sub(pattern, ":", text)
    return x

print("Task6")
print(Task6('hello'))
print(Task6('hello, world'))
print(Task6('Hi. Bye'))
print("-"*50)

#7
"""Write a python program to convert snake case string to camel case string."""
def Task7(text):
    def to_upper(match):
        return match.group(1).upper()
    
    result = re.sub(r'_([a-z])', to_upper, text)
    return result

print("Task7")
print(Task7('hello_world'))
print(Task7('hi_bye'))
print(Task7('vau'))
print("-"*50)


#8
"""Write a Python program to split a string at uppercase letters."""
def Task8(text):
    pattern = r"(?=[A-Z])"
    result = re.split(pattern, text)
    return [word for word in result if word]

print("Task8")
print(Task8("HelloWorld"))
print(Task8("Helloworld"))
print("-"*50)

#9
"""Write a Python program to insert spaces between words starting with capital letters."""
def Task9(text):
    pattern = r"([a-z])([A-Z])"
    result = re.sub(pattern, r"\1 \2", text)
    return result

print("Task9")
print(Task9("HelloWorld"))
print(Task9("HelloworldBye"))
print(Task9("HelloWorldBye"))
print("-"*50)

#10
"""Write a Python program to convert a given camel case string to snake case."""
def Task10(text):
    pattern = r"([a-z])([A-Z])"
    result = re.sub(pattern, r"\1_\2", text)
    return result.lower()

print("Task10")
print(Task10("HelloWorld"))        
print(Task10("HelloWorldBye"))      
print(Task10("camelCaseExample"))   
print("-" * 50)
    