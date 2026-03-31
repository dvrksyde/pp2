# read_files.py

from traceback import print_exc

file_path = "example.txt"

# read() – read entire file
with open(file_path, "r") as f:
    content = f.read()
    print("read():")
    print(content)

# readline() – read lines one by one
with open(file_path, "r") as f:
    line = f.readline()
    line = f.readline()  # Read the second line
    print("readline():")
    print(line)

# readlines() – list of lines separated by newline character
with open(file_path, "r") as f:
    lines = f.readlines()
    print("readlines():")
    print(lines)
