# Dataclass to be CLI and logger compatible

This package does only two things:

1. it takes a dataclass and converts it to a command line str.
2. it takes a dataclass and converts it to a loggable dict for 3rd party logging like [MLFlow](https://mlflow.org/).
Contrary to `asdict` it also converts nested dataclasses by separting their attributes by prefix.

By inheriting from the class `ReverseCli` you can use the `to_command_string` method to get the command line str and the property `loggable_dict` to get the loggable dict.

## Example

```python
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

parameters = Nested(a=1, b=Parameters(a=1, b="2", c=True, d=[3, 4]))
print(parameters.to_command_string())
# --a 1 --b.a 1 --b.b 2 --b.c --b.d 3 --b.d 4
print(parameters.loggable_dict)
# {'a': 1, 'b.a': 1, 'b.b': '2', 'b.c': True, 'b.d': [3, 4]}
```

## Installation

We use [UV](https://docs.astral.sh/uv/) for installation and [RUFF](https://docs.astral.sh/ruff/) for formating and linting.
