"""
MIT License

Copyright (c) 2024-present Isabelle Phoebe <izzy@uwu.gal>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Iterator,
    Literal,
    overload,
)

from httpcord.attachment import Attachment
from httpcord.channel import BaseChannel
from httpcord.enums import ApplicationCommandOptionType
from httpcord.locale import DEFAULT_LOCALE, Locale
from httpcord.role import Role
from httpcord.user import User


__all__: tuple[str, ...] = (
    "CommandOption",
    "Choice",
)


class CommandOption:
    __slots__ = (
        "_name",
        "_description",
        "_type",
        "_native_type",
        "_required",
        "_autocomplete",
        "_options",
        "_choices",
        "_min_value",
        "_max_value",
        "_min_length",
        "_max_length",
        "_locale",
    )

    if TYPE_CHECKING:
        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.SUB_COMMAND],
            native_type: None,
            required: None = ...,
            autocomplete: Literal[False] | None = ...,
            options: dict[str, CommandOption] | None = ...,
            choices: None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: None = ...,
            max_length: None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.SUB_COMMAND_GROUP],
            native_type: None,
            required: None = ...,
            autocomplete: None = ...,
            options: dict[str, CommandOption] = ...,
            choices: None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: None = ...,
            max_length: None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.STRING],
            native_type: str,
            required: bool | None = ...,
            autocomplete: Literal[False] | None = ...,
            options: None = ...,
            choices: list[Choice] | None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: int | None = ...,
            max_length: int | None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.STRING],
            native_type: str,
            required: bool | None = ...,
            autocomplete: Literal[True] = ...,
            options: None = ...,
            choices: None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: int | None = ...,
            max_length: int | None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.INTEGER],
            native_type: int,
            required: bool | None = ...,
            autocomplete: Literal[False] | None = ...,
            options: None = ...,
            choices: list[Choice] | None = ...,
            min_value: int | None = ...,
            max_value: int | None = ...,
            min_length: None = ...,
            max_length: None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.INTEGER],
            native_type: int,
            required: bool | None = ...,
            autocomplete: Literal[True] = ...,
            options: None = ...,
            choices: None = ...,
            min_value: int | None = ...,
            max_value: int | None = ...,
            min_length: None = ...,
            max_length: None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.NUMBER],
            native_type: float,
            required: bool | None = ...,
            autocomplete: Literal[False] | None = ...,
            options: None = ...,
            choices: list[Choice] | None = ...,
            min_value: float | None = ...,
            max_value: float | None = ...,
            min_length: None = ...,
            max_length: None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.NUMBER],
            native_type: float,
            required: bool | None = ...,
            autocomplete: Literal[True] = ...,
            options: None = ...,
            choices: None = ...,
            min_value: float | None = ...,
            max_value: float | None = ...,
            min_length: None = ...,
            max_length: None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[
                ApplicationCommandOptionType.BOOLEAN,
                ApplicationCommandOptionType.USER,
                ApplicationCommandOptionType.CHANNEL,
                ApplicationCommandOptionType.ROLE,
                ApplicationCommandOptionType.MENTIONABLE,
                ApplicationCommandOptionType.ATTACHMENT,
            ],
            native_type: bool | User | BaseChannel | Role | Attachment,
            required: bool | None = ...,
            autocomplete: None = ...,
            options: None = ...,
            choices: None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: None = ...,
            max_length: None = ...,
            locale: Locale | None = ...,
        ) -> None: ...

    def __init__(
        self,
        name: str,
        description: str | None,
        type: ApplicationCommandOptionType,
        native_type: str | int | float | bool | User | BaseChannel | Role | Attachment | None = None,
        required: bool | None = False,
        autocomplete: bool | None = False,
        options: dict[str, CommandOption] | None = None,
        choices: list[Choice] | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        locale: Locale | None = None,
    ) -> None:
        self._name: str = name
        self._description: str | None = description
        self._type: ApplicationCommandOptionType = type
        self._native_type: str | int | float | bool | User | BaseChannel | Role | Attachment | None = native_type
        self._required: bool = required or False
        self._autocomplete: bool | None = autocomplete
        self._options: dict[str, CommandOption] | None = options
        self._choices: list[Choice] | None = choices
        self._min_value: int | float | None = min_value
        self._max_value: int | float | None = max_value
        self._min_length: int | None = min_length
        self._max_length: int | None = max_length
        self._locale = locale or Locale(
            name_localisations={DEFAULT_LOCALE: name},
            description_localisations=(
                {DEFAULT_LOCALE: self._description}
                if self._description is not None
                else None
            ),
        )

    @property
    def description(self) -> str:
        """The description of the command option."""
        return self._description or "--"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "description": self.description,
            "type": self._type.value,
            "required": self._required if self._type not in [
                ApplicationCommandOptionType.SUB_COMMAND,
                ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            ] else None,
            "autocomplete": self._autocomplete,
            "options": [option.to_dict() for option in self._options.values()] if self._options else None,
            "choices": [choice.to_dict() for choice in self._choices] if self._choices else None,
            "min_value": self._min_value,
            "max_value": self._max_value,
            "min_length": self._min_length,
            "max_length": self._max_length,
            "name_localizations": self._locale.name_localisations,
            "description_localizations": self._locale.description_localisations,
        }

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield from self.to_dict().items()


class Choice:
    __slots__ = (
        "_name",
        "_value",
    )

    def __init__(self, name: str, value: str) -> None:
        self._name: str = name
        self._value: str = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "value": self._value,
        }

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield from self.to_dict().items()
