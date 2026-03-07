# copy_delete_files.py

import os
import shutil
from pathlib import Path

source = "write_example.txt"
copy_name = "copy_example.txt"

# Copy file
shutil.copy(source, copy_name)
print("File copied")

# Check if file exists
if os.path.exists(copy_name):
    print("Copy exists")

# Using pathlib
path = Path(copy_name)

print("File name:", path.name)
print("Absolute path:", path.resolve())

# Delete file
os.remove(copy_name)
print("File deleted")
# move_files.py
source = "write_example.txt"
destination_folder = "parent/child"

# ensure folder exists
os.makedirs(destination_folder, exist_ok=True)

# move file
shutil.move(source, destination_folder)

print("File moved to:", destination_folder)
