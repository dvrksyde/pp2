# write_files.py

# w – overwrite file
with open("write_example.txt", "w") as f:
    f.write("Hello\n")
    f.write("Python File Handling\n")

# a – append
with open("write_example.txt", "a") as f:
    f.write("This line is appended\n")

# x – create new file (error if exists)
try:
    with open("new_file.txt", "x") as f:
        f.write("File created using x mode")
except FileExistsError:
    print("File already exists")
