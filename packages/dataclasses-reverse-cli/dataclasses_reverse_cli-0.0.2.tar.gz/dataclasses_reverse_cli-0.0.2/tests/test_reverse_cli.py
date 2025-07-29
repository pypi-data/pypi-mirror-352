import unittest
from dataclasses import dataclass

from dataclasses_reverse_cli.reverse_cli import ReverseCli


@dataclass(kw_only=True)
class Parameters(ReverseCli):
    a: int
    b: str
    c: bool
    d: list[int]


@dataclass(kw_only=True)
class Nested(ReverseCli):
    a: int
    b: Parameters


class TestReverseCli(unittest.TestCase):
    def test_reverse_cli(self):
        parameters = Parameters(a=1, b="2", c=True, d=[3, 4])
        self.assertEqual(parameters.to_command_string(), " --a 1 --b 2 --c --d 3 4")

    def test_nested(self):
        parameters = Nested(a=1, b=Parameters(a=1, b="2", c=True, d=[3, 4]))
        self.assertEqual(
            parameters.to_command_string(), " --a 1 --b.a 1 --b.b 2 --b.c --b.d 3 4"
        )
