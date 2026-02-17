class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)

class Student(Person):
    pass

x = Student("Mike", "Olsen")
x.printname()

class Employee(Person):
    def __init__(self, fname, lname, job):
        super().__init__(fname, lname)
        self.job = job

    def show_job(self):
        print(self.firstname, "works as", self.job)

emp = Employee("Sara", "Smith", "Engineer")
emp.printname()
emp.show_job()

class AdvancedStudent(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.graduationyear = year

    def welcome(self):
        print(
            "Welcome", self.firstname, self.lastname, "to the class of", self.graduationyear
        )

stu = AdvancedStudent("Emma", "Stone", 2023)
stu.welcome()