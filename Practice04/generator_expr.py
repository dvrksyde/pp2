string = "geek"

reverse_gen = (string[i] for i in range(len(string) - 1, -1, -1))
reverse_list = list(reverse_gen)

print(reverse_list)


squares_list = [x * x for x in range(5)]
squares_gen = (x * x for x in range(5))

print(squares_list)
print(list(squares_gen))
