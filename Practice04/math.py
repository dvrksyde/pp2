import math


def to_radian(n):
    return n * math.pi


def trap_area(n, m, k):
    return (n + k) / 2 * m


def pol_area(n, m):
    return (n * (m**2)) / (4 * math.tan(math.pi / n))


def par_area(n, m):
    return n * m


n = int(input())
m = int(input())
k = int(input())
