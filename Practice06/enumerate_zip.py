# enumerate_zip_examples.py

names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

# enumerate
print("Enumerate:")
for index, name in enumerate(names):
    print(index, name)

print()

# zip
print("Zip:")
for name, score in zip(names, scores):
    print(name, score)

print()

# sorted
numbers = [5, 2, 9, 1]
print("Sorted:", sorted(numbers))

# len
print("Length:", len(names))

# type conversion
num_str = "100"
num_int = int(num_str)

print("Converted:", num_int, type(num_int))
