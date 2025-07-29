from fastapi import APIRouter, HTTPException

from src.core import calculator

calculator_router = APIRouter()


@calculator_router.get("/add")
def add(a: float, b: float):
    """
    Endpoint to add two numbers.

    Args:
        a (float): The first number to add.
        b (float): The second number to add.

    Returns:
        dict: The result of the addition.
    """
    result = calculator.add(a, b)
    return {"result": result}


@calculator_router.get("/subtract")
def subtract(a: float, b: float):
    """
    Endpoint to subtract two numbers.

    Args:
        a (float): The number to subtract from.
        b (float): The number to subtract.

    Returns:
        dict: The result of the subtraction.
    """
    result = calculator.subtract(a, b)
    return {"result": result}


@calculator_router.get("/multiply")
def multiply(a: float, b: float):
    """
    Endpoint to multiply two numbers.

    Args:
        a (float): The first number to multiply.
        b (float): The second number to multiply.

    Returns:
        dict: The result of the multiplication.
    """
    result = calculator.multiply(a, b)
    return {"result": result}


@calculator_router.get("/divide")
def divide(a: float, b: float):
    """
    Endpoint to divide two numbers.

    Args:
        a (float): The numerator.
        b (float): The denominator.

    Returns:
        dict: The result of the division.

    Raises:
        HTTPException: If division by zero is attempted.
    """
    try:
        result = calculator.divide(a, b)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
