
from utils import calculate_sum, calculate_product

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
    
    def add(self, a, b):
        """Add two numbers."""
        result = calculate_sum(a, b)
        self.history.append(f"Added {a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        result = calculate_product(a, b)
        self.history.append(f"Multiplied {a} * {b} = {result}")
        return result
    
    def get_history(self):
        """Get calculation history."""
        return self.history
