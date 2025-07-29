import math

def fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n (int): The position in the Fibonacci sequence (0-based)
    
    Returns:
        int: The nth Fibonacci number
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def fibonacci_sequence(n):
    """
    Generate a sequence of Fibonacci numbers up to the nth number.
    
    Args:
        n (int): The length of the sequence to generate
    
    Returns:
        list: A list containing the first n Fibonacci numbers
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence

def is_fibonacci(num):
    """
    Check if a number is a Fibonacci number.
    
    Args:
        num (int): The number to check
    
    Returns:
        bool: True if the number is Fibonacci, False otherwise
    """
    if num < 0:
        return False
    # A number is Fibonacci if and only if one of (5*n^2 + 4) or (5*n^2 - 4) is a perfect square
    val = 5 * num * num
    return math.isqrt(val + 4) ** 2 == val + 4 or math.isqrt(val - 4) ** 2 == val - 4