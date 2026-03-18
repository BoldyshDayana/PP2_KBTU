"""Find files by extension
Move/copy files between directories"""

import shutil
from pathlib import Path

source = Path("sample_data.txt")
destination = Path("projects/python/exercises/sample_moved.txt")

if not source.exists():
    source.write_text("Test data")

def copy_file():
    shutil.copy(source, destination)
    print(f"File copied to: {destination}")

def move_file():
    target_move = Path("projects/python/exercises/final_exercise.txt")
    destination.rename(target_move)
    print(f"File was moved to: {target_move}")

print("Options:")
print("1 - Copy File")
print("2 - Move file")
s = input("Choose option: ")
if s == "1":
    copy_file()
elif s == "2":
    move_file()
else:
    print("ERROR")




    