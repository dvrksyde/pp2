# map_filter_reduce.py

from functools import reduce

numbers = [1, 2, 3, 4, 5]

# map
squares = list(map(lambda x: x**2, numbers))
print("Squares:", squares)

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
