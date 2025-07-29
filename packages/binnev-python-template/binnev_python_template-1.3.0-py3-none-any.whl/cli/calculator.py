"""
This module provides CLI commands for performing basic arithmetic operations.

It uses the `typer` library to define commands for addition, subtraction,
multiplication, and division. Each command takes two numbers as input and prints
the result to the console.

The module relies on the `core.calculator` module for the actual arithmetic
operations.
"""

from typing import Optional

import typer

from src import core
from src.core import calculator

app = typer.Typer()


@app.command()
def add(a: float, b: float) -> None:
    """
    Add two numbers.

    Args:
        a (float): The first number to add.
        b (float): The second number to add.
    """
    result = calculator.add(a, b)
    typer.echo(f"The result of addition is: {result}")


@app.command()
def subtract(a: float, b: float) -> None:
    """
    Subtract two numbers.

    Args:
        a (float): The number to subtract from.
        b (float): The number to subtract.
    """
    result = calculator.subtract(a, b)
    typer.echo(f"The result of subtraction is: {result}")


@app.command()
def multiply(a: float, b: float) -> None:
    """
    Multiply two numbers.

    Args:
        a (float): The first number to multiply.
        b (float): The second number to multiply.
    """
    result = calculator.multiply(a, b)
    typer.echo(f"The result of multiplication is: {result}")


@app.command()
def divide(a: float, b: float) -> None:
    """
    Divide two numbers.
    Args:
        a (float): The numerator.
        b (float): The denominator.
    """
    try:
        result = calculator.divide(a, b)
        typer.echo(f"The result of division is: {result}")
    except ValueError as e:
        typer.echo(f"Error: {e}")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{core.__app_name__} v{core.__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Handles the --version flag"""
    return
