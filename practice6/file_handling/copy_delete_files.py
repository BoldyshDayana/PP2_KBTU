"""Delete files safely"""

import os

if os.path.exists('sample.txt'):
    os.remove('sample.txt')
    print("File was deleted")
else:
    print("File not found")

