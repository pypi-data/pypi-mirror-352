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

import io
import os


__all__: tuple[str, ...] = (
    "File",
)


class File:
    __slots__: tuple[str, ...] = (
        "_description",
        "_filename",
        "_spoiler",
        "_fp",
        "_data",
    )

    def __init__(
        self,
        fp: os.PathLike | io.BufferedIOBase,
        filename: str,
        description: str | None = None,
        spoiler: bool = False,
    ) -> None:
        self._data: bytes | None = None
        self._fp: os.PathLike | io.BufferedIOBase = fp
        self._filename: str = filename
        self._description: str | None = description
        self._spoiler: bool = spoiler

    @property
    def description(self) -> str | None:
        """The description of the file."""
        return self._description

    @property
    def filename(self) -> str:
        """The name of the file."""
        return self._filename

    @property
    def spoiler(self) -> bool:
        """Whether the file is a spoiler."""
        return self._spoiler

    def read(self) -> bytes:
        """Read the file's content."""
        if self._data is not None:
            return self._data
        if isinstance(self._fp, os.PathLike):
            with open(self._fp, "rb") as f:
                self._data = f.read()
                return self._data
        elif isinstance(self._fp, io.BufferedIOBase):
            self._data = self._fp.read()
            return self._data
        else:
            raise TypeError("File pointer must be a PathLike or BufferedIOBase instance.")

