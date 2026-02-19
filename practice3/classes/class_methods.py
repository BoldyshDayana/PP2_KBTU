#Methods are functions that belong to a class. 
#They define the behavior of objects created from the class.
#Functions

#1
class Person:
  def __init__(self, name):
    self.name = name

  def greet(self): #All methods must have self as the first parameter
    print("Hello, my name is " + self.name)

example = Person("Dayana")
example.greet()


#2
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b != 0:
            return a / b
        else:
            return "Error"

calc = Calculator()
print("10 + 5 =", calc.add(10, 5))
print("10 - 5 =", calc.subtract(10, 5))
print("10 × 5 =", calc.multiply(10, 5))
print("10 ÷ 5 =", calc.divide(10, 5))
print("10 ÷ 0 =", calc.divide(10, 0))


#3
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

  def __str__(self): #Returns a string representation when print() is called
    return f"{self.name} {self.age}"

e1 = Person("Dayana", 18)
print(e1)


#4
class TodoList:
    def __init__(self, name):
        self.name = name
        self.tasks = []  # Empty list to store tasks

    def add_task(self, task):
        self.tasks.append(task) #Add a new task to the list
        print(f"Added: {task}")

    def complete_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task) #Mark a task as complete (remove it)
            print(f"Completed: {task}")
        else:     
            print(f"Task not found: {task}")

    def show_tasks(self):
        print(f" {self.name} To-Do List:") #Display all tasks
        if not self.tasks:
            print("No tasks - you're all done!")
        else:
            for i, task in enumerate(self.tasks, 1):
                print(f"  {i}. {task}")

# Create and use todo list
my_todo = TodoList("Daily")
my_todo.add_task("Buy groceries")
my_todo.add_task("Finish homework")
my_todo.add_task("Call mom")
my_todo.show_tasks()
my_todo.complete_task("Buy groceries")
my_todo.show_tasks()