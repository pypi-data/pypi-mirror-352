import argparse, subprocess

from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

from utils.console import console, error
from utils.loader import load_config
from utils.parser import parse_extra, parse_command, parse_filename
from utils.selector import select


def main():
    parser = argparse.ArgumentParser(
        description="Run commands from `.yaml` files using unrun.",
        epilog="Example: unrun my_command",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("key", nargs="?", default=None, help="The key of the command to run from `.yaml`")
    parser.add_argument("--file", "-f", default=None, help="Path to the `.yaml`")
    parser.add_argument("extra", nargs="*", help="Extra arguments to pass to the command")
    args, unknown = parser.parse_known_args()

    key, file = args.key, args.file
    extra = parse_extra(args.extra, unknown)

    filename = parse_filename(file)

    config = load_config(filename)
    if config is None:
        return

    commands = parse_command(key, config)
    if commands is None:
        return

    command = select(commands)
    if command is None:
        console.print(
            Panel(
                Text("No command selected. Exiting.", style="bold yellow"),
                title=Text("No Command Selected", style="bold yellow")
            )
        )
        return

    if extra:
        command += f" {extra}"

    console.print(
        Panel(
            Syntax(command, "bash", word_wrap=True),
            title=Text(f"Running command for key '{args.key}'", style="bold blue"),
        )
    )

    try:
        subprocess.run(command, shell=True)
    except Exception as e:
        error(
            f"An unexpected error occurred: {e}",
            title="Unexpected Error"
        )
