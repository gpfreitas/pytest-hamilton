"""Console script for pytest_hamilton."""

import typer
from rich.console import Console

from pytest_hamilton import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for pytest_hamilton."""
    console.print("Replace this message by putting your code into "
               "pytest_hamilton.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
