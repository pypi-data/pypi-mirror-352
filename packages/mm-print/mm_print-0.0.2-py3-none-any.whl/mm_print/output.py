import sys
from collections.abc import Callable
from typing import Any, NoReturn

import rich
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from .serialization import to_json


def fatal(message: str, code: int = 1) -> NoReturn:
    """Print error message and exit with code."""
    print(message, file=sys.stderr)  # noqa: T201
    sys.exit(code)


def print_plain(messages: object) -> None:
    """Print to stdout without any formatting."""
    print(messages)  # noqa: T201


def print_json(data: object, default_serializer: Callable[[object], str] | None = None) -> None:
    """Print object as formatted JSON."""
    rich.print_json(to_json(data, default=default_serializer))


def print_table(title: str, columns: list[str], rows: list[list[Any]]) -> None:
    """Print data as a formatted table."""
    table = Table(*columns, title=title)
    for row in rows:
        table.add_row(*(str(cell) for cell in row))
    console = Console()
    console.print(table)


def pretty_print_toml(data: str, line_numbers: bool = False, theme: str = "monokai") -> None:
    """Print TOML with syntax highlighting."""
    console = Console()
    syntax = Syntax(data, "toml", theme=theme, line_numbers=line_numbers)
    console.print(syntax)
