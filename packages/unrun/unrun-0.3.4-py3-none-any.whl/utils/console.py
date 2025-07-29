from rich.console import Console
from rich.panel import Panel
from rich.text import Text


console = Console()


def template(message: str, title: str, color: str) -> None:
    console.print(
        Panel(
            Text(message, style=color),
            title=Text(title, style=f"bold {color}")
        )
    )


def success(message: str, title: str = "Success") -> None:
    template(message, title, "green")


def warning(message: str, title: str = "Warning") -> None:
    template(message, title, "yellow")


def error(message: str, title: str = "Error") -> None:
    template(message, title, "red")


def info(message: str, title: str = "Info") -> None:
    template(message, title, "blue")
