x = lambda a: a + 10
print(x(5))

multiply = lambda a, b: a * b
print(multiply(5, 6))

summation = lambda a, b, c: a + b + c
print(summation(5, 6, 2))

def myfunc(n):
    return lambda a: a * n

doubler = myfunc(2)
print(doubler(11))

tripler = myfunc(3)
print(tripler(11))

numbers = [1, 2, 3, 4, 5]

doubled = list(map(lambda x: x * 2, numbers))
print("Doubled:", doubled)

odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))
print("Odd:", odd_numbers)

students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]
sorted_students = sorted(students, key=lambda x: x[1])
print("Sorted by age:", sorted_students)

words = ["apple", "pie", "banana", "cherry"]
sorted_words = sorted(words, key=lambda x: len(x))
print("Sorted by length:", sorted_words)
