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

from typing import Any, Final


__all__: Final[tuple[str, ...]] = (
    "Embed",
)


class EmbedFooter:
    __slots__: Final[tuple[str, ...]] = (
        "text",
        "icon_url",
    )

    def __init__(
        self,
        *,
        text: str,
        icon_url: str | None = None,
    ) -> None:
        self.text = text
        self.icon_url = icon_url

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "icon_url": self.icon_url,
        }


class EmbedField:
    __slots__: Final[tuple[str, ...]] = (
        "name",
        "value",
        "inline",
    )

    def __init__(
        self,
        *,
        name: str | None = None,
        value: str | None = None,
        inline: bool = False,
    ) -> None:
        self.name = name
        self.value = value
        self.inline = inline

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "inline": self.inline,
        }


class Embed:
    __slots__: Final[tuple[str, ...]] = (
        "title",
        "description",
        "colour",
        "_fields",
        "_footer",
    )

    def __init__(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        colour: int | None = None,
    ) -> None:
        self.title = title
        self.description = description
        self.colour = colour
        self._fields: list[EmbedField] = []
        self._footer: EmbedFooter | None = None

    def add_field(
        self,
        *,
        name: str | None = None,
        value: str | None = None,
        inline: bool = False,
    ) -> None:
        self._fields.append(EmbedField(
            name=name,
            value=value,
            inline=inline,
        ))

    def set_footer(
        self,
        text: str,
        *,
        icon_url: str | None = None,
    ) -> None:
        self._footer = EmbedFooter(
            text=text,
            icon_url=icon_url,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "color": self.colour,
            "footer": (
                {} if not self._footer
                else self._footer.to_dict()
            ),
            "fields": [f.to_dict() for f in self._fields],
        }
