from typer.testing import CliRunner

from src.cli.calculator import app
from src.core import __version__

runner = CliRunner()


def test_add_command():
    result = runner.invoke(app, ["add", "2", "3"])
    assert result.exit_code == 0
    assert result.output.strip() == "The result of addition is: 5.0"


def test_subtract_command():
    result = runner.invoke(app, ["subtract", "5", "3"])
    assert result.exit_code == 0
    assert result.output.strip() == "The result of subtraction is: 2.0"


def test_multiply_command():
    result = runner.invoke(app, ["multiply", "4", "3"])
    assert result.exit_code == 0
    assert result.output.strip() == "The result of multiplication is: 12.0"


def test_divide_command():
    result = runner.invoke(app, ["divide", "10", "2"])
    assert result.exit_code == 0
    assert result.output.strip() == "The result of division is: 5.0"


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"python-template v{__version__}"
