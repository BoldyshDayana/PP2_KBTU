#1
i = 0
while i < 5:
  i += 1
  if i == 3:
    continue
  print(i)

#2
i = 0
while i < 10:
    i += 1
    if i % 2 == 1:  
        continue
    print(i)

#3
i = 0
while i < 12:
    i += 1
    if i % 3 == 0:
        continue
    print(i)

#4
hour = 9 
while hour <= 17:  
    if hour == 13:  
        hour += 1
        continue
    print(f"{hour}:00 - Working")
    hour += 1

#5
grades = ["A", "F", "B", "C", "F", "A"]
i = 0

while i < len(grades):
    if grades[i] == "F":
        i += 1
        continue
    print(f"Good grade: {grades[i]}")
    i += 1