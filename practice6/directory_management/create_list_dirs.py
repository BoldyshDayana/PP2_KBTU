"""Create nested directories
List files and folders"""

import os

#Using os.makedirs() - creates all intermediate directories
os.makedirs('projects/python/exercises', exist_ok=True)
print("Nested directories created: projects/python/exercises")

#Using pathlib (modern approach)
from pathlib import Path
Path('photos/vacation/Bulgaria').mkdir(parents=True, exist_ok=True)
print("Nested directories created: photos/vacation/Bulgaria")



def list_directory_contents(path='.'):

    print("-" * 50)
    
    print("\nDetailed listing:")
    for item in Path(path).iterdir():
        if item.is_dir():
            print(f"Directory: {item.name}/")
        else:
            modified = item.stat().st_mtime
            print(f"File: {item.name} (modified: {modified})")
    
    # List only directories
    print("\nDirectories only:")
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    for d in dirs:
        print(f"{d}/")
    
    # List only files
    print("\nFiles only:")
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for f in files:
        print(f"{f}")


list_directory_contents('.')