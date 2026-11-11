import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_CALC_PATH = Path(__file__).resolve().parent.parent / "examples" / "calculator" / "calc.py"
_spec = importlib.util.spec_from_file_location("calc", _CALC_PATH)
assert _spec is not None and _spec.loader is not None
calc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(calc)


def test_add():
    assert calc.add(3, 4) == 7


def test_subtract():
    assert calc.subtract(3, 4) == -1


def test_multiply():
    assert calc.multiply(3, 4) == 12


def test_divide():
    assert calc.divide(7, 2) == 3.5


def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        calc.divide(1, 0)


def test_parse_number_int_and_float():
    assert calc.parse_number("3") == 3
    assert isinstance(calc.parse_number("3"), int)
    assert calc.parse_number("2.5") == 2.5


@pytest.mark.parametrize("text", ["abc", "nan", "NaN", "inf", "-inf", "1e400"])
def test_parse_number_invalid(text):
    with pytest.raises(ValueError):
        calc.parse_number(text)


def test_format_result_integral_float():
    assert calc.format_result(2.0) == "2"
    assert calc.format_result(3.5) == "3.5"


def test_main_success_prints_result(capsys):
    assert calc.main(["3", "+", "4"]) == 0
    assert capsys.readouterr().out.strip() == "7"


def test_main_negative_operand(capsys):
    assert calc.main(["-3", "+", "4"]) == 0
    assert capsys.readouterr().out.strip() == "1"


def test_main_x_alias_multiplies(capsys):
    assert calc.main(["3", "x", "4"]) == 0
    assert capsys.readouterr().out.strip() == "12"


def test_main_division_by_zero(capsys):
    assert calc.main(["1", "/", "0"]) == 1
    captured = capsys.readouterr()
    assert "division by zero" in captured.err
    assert captured.out == ""


def test_main_invalid_number(capsys):
    assert calc.main(["abc", "+", "1"]) == 1
    captured = capsys.readouterr()
    assert "abc" in captured.err
    assert captured.out == ""


def test_main_unknown_operator(capsys):
    assert calc.main(["1", "%", "2"]) == 1
    captured = capsys.readouterr()
    assert "%" in captured.err
    assert "supported operators: + - * x /" in captured.err
    assert captured.out == ""


def test_main_wrong_arg_count(capsys):
    assert calc.main(["1", "+"]) == 2
    assert "usage:" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["3", "*", "4"], "12"),
        (["4", "/", "2"], "2"),
        (["-3", "-", "-4"], "1"),
        (["0.5", "+", "0.25"], "0.75"),
        (["1e3", "+", "1"], "1001"),
        (["9007199254740993", "/", "1"], "9007199254740993"),
    ],
)
def test_main_results(capsys, args, expected):
    assert calc.main(args) == 0
    assert capsys.readouterr().out.strip() == expected


def test_divide_huge_exact_ints_stays_exact():
    big = 10**400
    assert calc.divide(big * 6, 3) == big * 2


@pytest.mark.parametrize(
    "args",
    [
        [str(10**400), "/", "3"],  # int too large to convert to float
        ["1e308", "x", "10"],  # float result overflows to inf
        ["1e308", "+", "1e308"],
    ],
)
def test_main_result_too_large(capsys, args):
    assert calc.main(args) == 1
    captured = capsys.readouterr()
    assert "result too large" in captured.err
    assert captured.out == ""


def test_script_exit_codes():
    script = str(_CALC_PATH)
    ok = subprocess.run([sys.executable, script, "3", "+", "4"], capture_output=True, text=True)
    assert (ok.returncode, ok.stdout.strip()) == (0, "7")
    bad = subprocess.run([sys.executable, script, "1", "/", "0"], capture_output=True, text=True)
    assert bad.returncode == 1
    usage = subprocess.run([sys.executable, script, "1"], capture_output=True, text=True)
    assert usage.returncode == 2
