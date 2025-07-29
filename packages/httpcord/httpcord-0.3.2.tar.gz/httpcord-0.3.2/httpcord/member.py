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

import datetime

from httpcord.asset import Asset
from httpcord.avatar import AvatarDecoration
from httpcord.user import User
from httpcord.utils.functions import from_timestamp


__all__: tuple[str, ...] = (
    "PartialMember",
    "PartialMemberWithUser",
    "Member",
)


class PartialMember:
    __slots__: tuple[str, ...] = (
        "_id",
        "_guild_id",
        "_avatar",
        "_avatar_decoration",
        "_banner",
        "_communication_disabled_until",
        "_flags",
        "_joined_at",
        "_nick",
        "_pending",
        "_permissions",
        "_premium_since",
        "_roles",
        "_unusual_dm_activity_until",
    )

    def __init__(self, data: dict, user_id: int, guild_id: int) -> None:
        self._id: int = user_id
        self._guild_id: int = guild_id
        self._avatar: str | None = data.get("avatar")
        self._avatar_decoration: dict | None = data.get("avatar_decoration_data")
        self._banner: str | None = data.get("banner")
        self._communication_disabled_until: datetime.datetime | None = from_timestamp(data["communication_disabled_until"]) if data.get("communication_disabled_until") else None
        self._flags: int = data.get("flags", 0)
        self._joined_at: datetime.datetime = from_timestamp(data["joined_at"])
        self._nick: str | None = data.get("nick")
        self._pending: bool = data.get("pending", False)
        self._permissions: int = int(data["permissions"])
        self._premium_since: datetime.datetime | None = (
            from_timestamp(data["premium_since"])
            if data.get("premium_since") else None
        )
        self._roles: list[int] = data["roles"]
        self._unusual_dm_activity_until: datetime.datetime | None = (
            from_timestamp(data["unusual_dm_activity_until"])
            if data.get("unusual_dm_activity_until") else None
        )

    @property
    def id(self) -> int:
        """The member's ID."""
        return self._id

    @property
    def guild_id(self) -> int:
        """The ID of the guild the member belongs to."""
        return self._guild_id

    @property
    def guild_avatar(self) -> Asset | None:
        """The member's guild avatar."""
        if self._avatar is None:
            return None
        return Asset(
            base_url=f"https://cdn.discordapp.com/guilds/{self.guild_id}/users/{self.id}/avatars",
            code=self._avatar,
        )

    @property
    def guild_avatar_decoration(self) -> AvatarDecoration | None:
        """The member's guild avatar decoration."""
        if self._avatar_decoration:
            return AvatarDecoration(self._avatar_decoration)
        return None

    @property
    def banner(self) -> Asset | None:
        """The member's banner."""
        if self._banner:
            return Asset(
                base_url=f"https://cdn.discordapp.com/banners/{self.id}",
                code=self._banner,
            )
        return None

    @property
    def communication_disabled_until(self) -> datetime.datetime | None:
        """The date until the member's communication is disabled."""
        return self._communication_disabled_until

    @property
    def flags(self) -> int:
        """The member's flags."""
        return self._flags

    @property
    def joined_at(self) -> datetime.datetime:
        """The date when the member joined the guild."""
        return self._joined_at

    @property
    def nick(self) -> str | None:
        """The member's nickname."""
        return self._nick

    @property
    def pending(self) -> bool:
        """Whether the member is pending."""
        return self._pending

    @property
    def permissions(self) -> int:
        """The member's permissions in the guild."""
        return self._permissions

    @property
    def premium_since(self) -> datetime.datetime | None:
        """The date when the member started boosting the guild."""
        return self._premium_since

    @property
    def roles(self) -> list[int]:
        """The member's roles in the guild."""
        return self._roles

    @property
    def unusual_dm_activity_until(self) -> datetime.datetime | None:
        """The date until the member's unusual DM activity is disabled."""
        return self._unusual_dm_activity_until


class PartialMemberWithUser(PartialMember):
    __slots__: tuple[str, ...] = (
        "_user",
    )

    def __init__(self, data: dict, guild_id: int) -> None:
        super().__init__(data, int(data["user"]["id"]), guild_id)
        self._user: User = User(data["user"])

    @property
    def user(self) -> User:
        """The member's user object."""
        return self._user


class Member(PartialMemberWithUser):
    __slots__: tuple[str, ...] = (
        "_deaf",
        "_mute",
    )

    def __init__(self, data: dict, guild_id: int) -> None:
        super().__init__(data, guild_id)
        self._deaf: bool | None = data.get("deaf")
        self._mute: bool | None = data.get("mute")

    @property
    def deaf(self) -> bool:
        """Whether the member is deafened."""
        return self._deaf or False

    @property
    def mute(self) -> bool:
        """Whether the member is muted."""
        return self._mute or False
