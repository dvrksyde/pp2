def square(n):
    for i in range(n):
        yield i * i


def even(n):
    for i in range(n):
        if i % 2 == 0:
            yield i


def is_devisible(n):
    for i in range(n):
        if i % 2 == 0 and i % 3 == 0:
            yield i


def squared(n, m):
    for i in range(n, m + 1):
        yield i * i


def up_to_down(n):
    for i in range(n, -1, -1):
        yield i


n = int(input())
