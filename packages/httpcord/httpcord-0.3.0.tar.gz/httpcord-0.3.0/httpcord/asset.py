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

__all__: tuple[str, ...] = (
    "Asset",
)


class Asset:
    __slots__: tuple[str, ...] = (
        "_base_url",
        "_code",
    )

    def __init__(self, base_url: str, code: str) -> None:
        self._base_url: str = base_url
        self._code: str = code

    @property
    def animated(self) -> bool:
        """Whether the avatar is animated."""
        return self.code.startswith("a_") if self._code else False

    @property
    def code(self) -> str:
        """The avatar code."""
        return self._code

    def url(self, *, animated: bool | None = None, size: int = 1024) -> str:
        """The URL of the avatar."""
        animated = self.animated if animated is None else animated
        return f"{self._base_url}/{self._code}.{'png' if not animated else 'gif'}?size={size}"
