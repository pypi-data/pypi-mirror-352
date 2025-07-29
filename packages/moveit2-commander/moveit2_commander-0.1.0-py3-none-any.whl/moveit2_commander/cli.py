"""Console script for moveit2_commander."""
import moveit2_commander

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for moveit2_commander."""
    console.print("Replace this message by putting your code into "
               "moveit2_commander.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
