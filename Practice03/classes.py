class MyClass:
    x = 5

p1 = MyClass()
print("Value of x:", p1.x)


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def say_hello(self):
        print("Hello, my name is", self.name)

p2 = Person("Alice", 30)
print(p2.name, p2.age)
p2.say_hello()


class Student:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)

x = Student("John", "Doe")
x.printname()