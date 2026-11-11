"""Tiny command-line calculator.

Usage:
    python calc.py <number> <op> <number>

Operators: + - * x /

Note: `*` is expanded by most shells, so quote it ("*") or use `x` as an alias.
Git Bash on Windows rewrites a bare `/` into a path (quoting does not help), so
there run with `MSYS_NO_PATHCONV=1`, or use PowerShell or cmd.

Examples:
    python calc.py 3 + 4
    python calc.py 3 "*" 4
    python calc.py 3 x 4
    python calc.py 7 / 2
"""

from __future__ import annotations

import math
import sys
from collections.abc import Callable

Number = int | float


def add(a: Number, b: Number) -> Number:
    return a + b


def subtract(a: Number, b: Number) -> Number:
    return a - b


def multiply(a: Number, b: Number) -> Number:
    return a * b


def divide(a: Number, b: Number) -> Number:
    if b == 0:
        raise ZeroDivisionError("division by zero")
    if isinstance(a, int) and isinstance(b, int) and a % b == 0:
        return a // b  # exact, and safe for ints too large for a float
    return a / b


OPERATIONS: dict[str, Callable[[Number, Number], Number]] = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "x": multiply,
    "/": divide,
}


def parse_number(text: str) -> Number:
    """Parse text as int, falling back to float. Rejects nan and inf."""
    try:
        return int(text)
    except ValueError:
        pass
    try:
        value = float(text)
    except ValueError:
        raise ValueError(f"invalid number: {text!r}") from None
    if not math.isfinite(value):
        raise ValueError(f"invalid number: {text!r}")
    return value


def format_result(value: Number) -> str:
    """Format a result, printing integral floats without a decimal part."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 3:
        print("usage: calc.py <number> <op> <number>", file=sys.stderr)
        return 2
    left_text, op, right_text = args
    try:
        left = parse_number(left_text)
        right = parse_number(right_text)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    func = OPERATIONS.get(op)
    if func is None:
        print(f"error: unknown operator: {op!r}", file=sys.stderr)
        print(f"supported operators: {' '.join(OPERATIONS)}", file=sys.stderr)
        return 1
    try:
        result = func(left, right)
    except ZeroDivisionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OverflowError:
        result = math.inf
    if isinstance(result, float) and not math.isfinite(result):
        print("error: result too large", file=sys.stderr)
        return 1
    print(format_result(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
