# read_files.py

from traceback import print_exc

file_path = "example.txt"

# read() – read entire file
with open(file_path, "r") as f:
    content = f.read()
    print("read():")
    print(content)

# readline() – read one line
with open(file_path, "r") as f:
    line = f.readline()
    print("readline():")
    print(line)

# readlines() – list of lines
with open(file_path, "r") as f:
    lines = f.readlines()
    print("readlines():")
    print(lines)
