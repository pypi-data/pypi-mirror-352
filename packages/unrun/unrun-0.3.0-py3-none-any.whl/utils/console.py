from rich.console import Console
from rich.panel import Panel
from rich.text import Text


console = Console()


def error(message: str, title: str = "Error") -> None:
    console.print(
        Panel(
            Text(message, style="bold red"),
            title=Text(title, style="bold red")
        )
    )
