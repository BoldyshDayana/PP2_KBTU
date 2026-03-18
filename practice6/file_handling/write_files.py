"""Append new lines and verify content
Copy and back up files using shutil"""

def append_to_file():
    
    with open("sample.txt", "a") as file:
        file.write("This line was added later.\n")
        file.write("File appending is useful!\n")
        file.write("End of appended content.\n")
    
    with open("sample.txt", "r") as file:
        print(file.read())

append_to_file()




import shutil
import os

def backup_files():
    
    #Simple copy
    shutil.copy("sample.txt", "sample_copy.txt")
    print("Simple copy created: sample_copy.txt")

backup_files()