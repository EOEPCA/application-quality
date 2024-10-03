#!/usr/bin/python3

import os
import sys  # Unused import to trigger a pylint warning

def add_numbers(a, b):
    """Adds two numbers and returns the result."""
    result = a + b
    return result

def greet_user(name):
    """Greets the user with their name."""
    greeting = f"Hello, {name}!"
    print(greeting)

def factorial(n):
    """Calculates the factorial of a number."""
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def display_info(self):
        """Displays the person's information."""
        print(f"Name: {self.name}, Age: {self.age}")

# Main execution
if __name__ == "__main__":
    greet_user("Alice")
    print(add_numbers(3, 5))

    p = Person("Bob", 30)
    p.display_info()

    print(f"The factorial of 5 is: {factorial(5)}")