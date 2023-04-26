#!/usr/bin/env python3
"""Scroll through all the source code in the project."""
import random
import argparse
from pathlib import Path
from time import sleep

from pygments import highlight
from pygments.formatters import TerminalFormatter  # pylint: disable=no-name-in-module
from pygments.lexers import PythonLexer  # pylint: disable=no-name-in-module

if __name__ != "__main__":
    from shiny_app.django_apps.functions.views import send_message


class PrintSource:
    """Print all the source code in the project."""

    def __init__(self, file_types: list[str] | None = None, source_code_root: Path | None = None, print_delay: float = 0.1):
        self.print_delay = print_delay
        self.line_number = 0

        self.file_types = file_types or ["*.py", "*.json", "*.html", "*.css", "*.js"]

        self.source_code_root = source_code_root or Path.home() / "VSCode" / "shiny_app"

        self.file_names = self.get_file_names()

    def scroll_source(self):
        """Scroll through all the source code in the project."""
        for file_name in self.file_names:
            with file_name.open("r", encoding="utf-8") as file:
                self.print_lines(file.readlines())

        self.line_number = 0

    def print_lines(self, lines: list[str]):
        """Print the lines of code in the terminal."""
        for file_line_number, code_line in enumerate(lines):
            if code_line.strip() == "":
                continue

            style = 1
            color = 32
            code_line_color = highlight(code_line, PythonLexer(), TerminalFormatter())
            print(f"\033[{style};{color}m{self.line_number}:{file_line_number}\033[15G{code_line_color}", end="")
            code_line = code_line.replace("\n", "")
            if __name__ != "__main__":
                send_message(f"{self.line_number}:{file_line_number}\t{code_line}")
            self.line_number += 1
            if self.line_number % 25 == 0:
                sleep(self.print_delay)

    def get_file_names(self) -> list[Path]:
        """Get all the file names in the project."""
        file_names = []
        for file_type in self.file_types:
            file_names.extend(self.source_code_root.rglob(file_type))
        return file_names

    def set_delay(self, min_delay: float = 0.1, max_delay: float = 2):
        """Set new delay between printing lines."""
        self.print_delay = random.uniform(min_delay, max_delay)

    def run_forever(self):
        """Start the program."""
        while True:
            self.set_delay()
            self.scroll_source()

    def run(self, loops: int = 1):
        """Start the program."""
        for _ in range(loops):
            self.set_delay()
            self.scroll_source()


def run(loops: int = 10, max_delay: float = 1):
    """Run."""
    printer = PrintSource()
    printer.set_delay(max_delay=max_delay)
    for _ in range(loops):
        printer.scroll_source()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("loops", type=int, default=1)
    arg_parser.add_argument("max_delay", type=float, default=2)
    args = arg_parser.parse_args()

    run(args.loops, args.max_delay)
