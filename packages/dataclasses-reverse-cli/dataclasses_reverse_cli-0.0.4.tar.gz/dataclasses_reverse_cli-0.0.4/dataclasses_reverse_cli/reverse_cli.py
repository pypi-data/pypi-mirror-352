import dataclasses
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


@dataclass(kw_only=True)
class ReverseCli:
    @staticmethod
    def _flatten(
        dictionary: dict[str, Any], parent_key: str = "", separator: str = "."
    ) -> dict[str, Any]:
        """
        This method takes in a dictionary `parent_key` infront of the keys of the
        dictionary.
        """
        items = []
        for key, value in dictionary.items():
            new_key = parent_key + separator + key if parent_key else key
            if isinstance(value, dict):
                items.extend(
                    ReverseCli._flatten(
                        value, new_key, separator=separator
                    ).items()
                )
            else:
                items.append((new_key, value))
        return dict(items)

    @property
    def loggable_dict(self) -> dict[str, Any]:
        return ReverseCli._flatten(asdict(self))

    def to_command_string(self, parameter_name: str = "") -> str:
        """
        Converts a dataclass into something that can be added to a tyro.cli parsable
        command. Note that this will fail for variables that are declared as bool
        without a default value.
        :return: string of the command parsed by tyro
        """
        if parameter_name != "":
            parameter_name += "."

        command_string = ""
        for attribute in dataclasses.fields(self):
            key_string = attribute.name.replace("_", "-")
            value = getattr(self, attribute.name)

            if isinstance(value, list) | isinstance(value, tuple):
                value_string = [str(x) for x in value]
                command_string += f" --{parameter_name}{key_string} " + " ".join(
                    value_string
                )
                continue

            if isinstance(value, bool) and value is True:
                command_string += f" --{parameter_name}{key_string}"
                continue

            if isinstance(value, bool) and value is False:
                command_string += f" --{parameter_name}no-{key_string}"
                continue

            if value == "":
                command_string += f" --{parameter_name}{key_string} ''"
                continue

            if isinstance(value, ReverseCli):
                command_string += value.to_command_string(
                    parameter_name=parameter_name + str(key_string)
                )
                continue

            if isinstance(value, Enum):
                command_string += f" --{parameter_name}{key_string} {value.name}"
                continue

            command_string += f" --{parameter_name}{key_string} {value}"

        return command_string
