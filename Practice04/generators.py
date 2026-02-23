def count_up_to(n):
    count = 1
    while count <= n:
        yield count
        count += 1


gen = count_up_to(5)

for num in gen:
    print(num)


def simple_generator():
    yield 1
    yield 2
    yield 3


g = simple_generator()

print(next(g))
print(next(g))
print(next(g))


def large_numbers():
    n = 0
    while True:
        yield n
        n += 1


gen = large_numbers()

print(next(gen))
print(next(gen))
print(next(gen))
