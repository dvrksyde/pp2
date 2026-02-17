def my_function():
    print("Hello from a function")

my_function()

def greet(name):
    print("Hello", name)

greet("Alice")

def add_numbers(a, b):
    return a + b

result = add_numbers(5, 7)
print("Sum is", result)

def test_scope():
    x = 10
    print("Inside function, x =", x)

test_scope()

def describe_pet(pet_name="Unknown"):
    print("I have a pet named", pet_name)

describe_pet("Buddy")
describe_pet()

def many_args(*args):
    for arg in args:
        print("Arg:", arg)

many_args(1, 2, 3)

def many_kwargs(**kwargs):
    for key, value in kwargs.items():
        print(key, "->", value)

many_kwargs(name="Bob", age=25)
