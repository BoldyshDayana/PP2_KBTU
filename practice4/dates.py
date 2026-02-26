#1
"""Write a Python program to subtract five days from current date."""
import datetime
from datetime import timedelta

current_date=datetime.date.today()
new_date=current_date-timedelta(days=5)
print(f"Current date: {current_date.strftime('%Y-%m-%d')}")
print(f"Date 5 days ago: {new_date.strftime('%Y-%m-%d')}")
print("-"*50)

#2
"""Write a Python program to print yesterday, today, tomorrow."""
current_date=datetime.date.today()
print(f"Yesterday: {(current_date-datetime.timedelta(days=1)).strftime("%d-%m-%Y")}")
print(f"Today: {current_date.strftime("%d-%m-%Y")}")
print(f"Tomorrow: {(current_date+datetime.timedelta(days=1)).strftime("%d-%m-%Y")}")
print("-"*50)


#3
"""Write a Python program to drop microseconds from datetime."""
now=datetime.datetime.today()
now_no_ms=now.replace(microsecond=0)
print(f"Original: {now}")
print(f"Without microseconds: {now_no_ms}")
print("-"*50)


#4
"""Write a Python program 
to calculate two date difference in seconds."""
now=datetime.datetime.now()
now_no_ms=now.replace(microsecond=0)
my_birthday=datetime.datetime(2007, 7, 24, 13, 48, 10)
difference=now_no_ms-my_birthday
seconds_difference=difference.total_seconds()
print(f"Start: {now_no_ms}")
print(f"End: {my_birthday}")
print(f"Difference in seconds: {int(seconds_difference)} seconds")