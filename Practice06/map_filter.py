# map_filter_reduce.py

from functools import reduce

numbers = [11, 12, 31, 44, 15]

# map
strt = list(map(lambda x: str(x)[0]=="1", numbers)).count(True)
print("Strt:", strt)

# filter
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", evens)

# reduce
total = reduce(lambda a, b: a + b, numbers)
print("Reduce sum:", total)

# built-in alternatives
print("Sum:", sum(numbers))
print("Min:", min(numbers))
print("Max:", max(numbers))
