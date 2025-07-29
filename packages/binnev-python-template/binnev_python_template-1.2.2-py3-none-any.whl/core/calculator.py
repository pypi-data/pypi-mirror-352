"""The core calculator library with basic arithmetic operations."""


def add(a: float, b: float) -> float:
    """
    Return the sum of two numbers.

    The `add` function is a simple utility designed to perform the addition of
    two floating-point numbers. It takes two arguments, `a` and `b`, both of
    which are expected to be of type `float`. The function returns their sum,
    also as a `float`.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of the two numbers.

    Examples:
        >>> add(2, 3)
        5

        >>> add(-1, 1)
        0
    """
    return a + b


def subtract(a: float, b: float) -> float:
    """
    Return the difference of two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The difference of the two numbers.

    Examples:
        >>> subtract(5, 3)
        2

        >>> subtract(2, 5)
        -3
    """
    return a - b


def multiply(a: float, b: float) -> float:
    """
    Return the product of two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of the two numbers.

    Examples:
        >>> multiply(2, 3)
        6

        >>> multiply(-1, 4)
        -4
    """
    return a * b


def divide(a: float, b: float) -> float:
    """
    Return the division of two numbers. Raise an error if dividing by zero.

    Args:
        a: The numerator.
        b: The denominator.

    Returns:
        The result of the division.

    Raises:
        ValueError: If the denominator is zero.

    Examples:
        >>> divide(6, 3)
        2.0

        >>> divide(5, 2)
        2.5
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
