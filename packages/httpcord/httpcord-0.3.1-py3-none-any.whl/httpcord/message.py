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

from httpcord.channel import BaseChannel


__all__: tuple[str, ...] = (
    "PartialMessage",
)


class PartialMessage:
    __slots__: tuple[str, ...] = (
        "_id",
        "_lobby_id",
        "_channel_id",
        "_type",
        "_content",
        "_author",
        "_flags",
        "_application_id",
        "_channel",
        "_recipient_id",
    )

    def __init__(self, data: dict) -> None:
        self._id: int = int(data["id"])
        self._lobby_id: str | None = data.get("lobby_id")
        self._channel_id: int = int(data["channel_id"])
        self._type: int | None = data.get("type")
        self._content: str = data["content"]
        self._author: dict = data["author"]
        self._flags: int | None = data.get("flags")
        self._application_id: str | None = data.get("application_id")
        self._channel: dict | None = data.get("channel")
        self._recipient_id: str | None = data.get("recipient_id")

    @property
    def id(self) -> int:
        """The message's ID."""
        return self._id

    @property
    def lobby_id(self) -> int | None:
        """The ID of the lobby this message belongs to, if applicable."""
        return int(self._lobby_id) if self._lobby_id is not None else None

    @property
    def channel_id(self) -> int:
        """The ID of the channel this message was sent in."""
        return self._channel_id

    @property
    def type(self) -> int | None:
        """The type of the message, if applicable."""
        return self._type

    @property
    def content(self) -> str:
        """The content of the message, if applicable."""
        return self._content

    @property
    def author(self) -> dict | None:
        """The author of the message, if applicable."""
        return self._author

    @property
    def flags(self) -> int | None:
        """The flags associated with the message."""
        return self._flags

    @property
    def application_id(self) -> int | None:
        """The ID of the application associated with the message, if applicable."""
        return int(self._application_id) if self._application_id is not None else None

    @property
    def channel(self) -> BaseChannel | None:
        """The channel the message was sent in, if applicable."""
        return BaseChannel.from_data(self._channel) if self._channel else None

    @property
    def recipient_id(self) -> int | None:
        """The ID of the recipient of the message, if applicable."""
        return int(self._recipient_id) if self._recipient_id is not None else None
