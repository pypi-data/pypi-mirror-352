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

from httpcord.asset import Asset
from httpcord.utils.functions import null_type_to_bool


__all__: tuple[str, ...] = (
    "Role",
)


class RoleColours:
    __slots__: tuple[str, ...] = (
        "_primary_colour",
        "_secondary_colour",
        "_tertiary_colour",
    )

    def __init__(self, data: dict) -> None:
        self._primary_colour: int = int(data["primary_color"])
        self._secondary_colour: int | None = int(data["secondary_color"])
        self._tertiary_colour: int | None = int(data["tertiary_color"])

    @property
    def primary_colour(self) -> int:
        """The primary colour of the role."""
        return self._primary_colour

    @property
    def secondary_colour(self) -> int | None:
        """The secondary colour of the role, if any."""
        return self._secondary_colour

    @property
    def tertiary_colour(self) -> int | None:
        """The tertiary colour of the role, if any."""
        return self._tertiary_colour


class RoleTags:
    __slots__: tuple[str, ...] = (
        "_bot_id",
        "_integration_id",
        "_premium_subscriber",
        "_subscription_listing_id",
        "_available_for_purchase",
        "_guild_connections",
    )

    def __init__(self, data: dict) -> None:
        self._bot_id: int | None = int(data.get("bot_id", 0))
        self._integration_id: int | None = data.get("integration_id")
        self._subscription_listing_id: int | None = int(data.get("subscription_listing_id", 0))
        self._premium_subscriber: bool = null_type_to_bool(data, "premium_subscriber")
        self._available_for_purchase: bool = null_type_to_bool(data, "available_for_purchase")
        self._guild_connections: bool = null_type_to_bool(data, "guild_connections")

    @property
    def bot_id(self) -> int | None:
        """The ID of the bot associated with the role, if any."""
        return self._bot_id

    @property
    def integration_id(self) -> int | None:
        """The ID of the integration associated with the role, if any."""
        return self._integration_id

    @property
    def subscription_listing_id(self) -> int | None:
        """The ID of the subscription listing associated with the role, if any."""
        return self._subscription_listing_id

    @property
    def premium_subscriber(self) -> bool:
        """Whether the role is associated with a premium subscriber."""
        return self._premium_subscriber

    @property
    def available_for_purchase(self) -> bool:
        """Whether the role is available for purchase."""
        return self._available_for_purchase


class Role:
    __slots__: tuple[str, ...] = (
        "_id",
        "_name",
        "_description",
        "_colour",
        "_colours",
        "_hoist",
        "_icon",
        "_unicode_emoji",
        "_position",
        "_permissions",
        "_managed",
        "_mentionable",
        "_flags",
        "_tags",
    )

    def __init__(self, data: dict) -> None:
        self._id: int = int(data["id"])
        self._name: str = data["name"]
        self._description: str | None = data.get("description")
        self._colour: int = int(data["color"])
        self._colours: dict | None = data.get("colours")
        self._hoist: bool = data["hoist"]
        self._icon: str | None = data.get("icon")
        self._unicode_emoji: str | None = data.get("unicode_emoji")
        self._position: int = int(data["position"])
        self._permissions: int = int(data["permissions"])
        self._managed: bool = data["managed"]
        self._mentionable: bool = data["mentionable"]
        self._flags: int | None = data.get("flags")
        self._tags: dict | None = data.get("tags")

    @property
    def id(self) -> int:
        """The role ID."""
        return self._id

    @property
    def name(self) -> str:
        """The name of the role."""
        return self._name

    @property
    def description(self) -> str | None:
        """The description of the role, if any."""
        return self._description

    @property
    def colour(self) -> int:
        """The colour of the role."""
        return self._colour

    @property
    def colours(self) -> RoleColours | None:
        """The role colours, if any."""
        if self._colours is not None:
            return RoleColours(self._colours)
        return None

    @property
    def hoist(self) -> bool:
        """Whether the role is hoisted in the sidebar."""
        return self._hoist

    @property
    def icon(self) -> Asset | None:
        """The icon of the role, if any."""
        if self._icon is not None:
            return Asset(
                base_url=f"https://cdn.discordapp.com/role-icons/{self.id}/{self._icon}",
                code=self._icon,
            )
        return None

    @property
    def unicode_emoji(self) -> str | None:
        """The Unicode emoji of the role, if any."""
        return self._unicode_emoji

    @property
    def position(self) -> int:
        """The position of the role in the role hierarchy."""
        return self._position

    @property
    def permissions(self) -> int:
        """The permissions of the role."""
        return self._permissions

    @property
    def managed(self) -> bool:
        """Whether the role is managed by an integration."""
        return self._managed

    @property
    def mentionable(self) -> bool:
        """Whether the role is mentionable."""
        return self._mentionable

    @property
    def flags(self) -> int | None:
        """The flags of the role, if any."""
        return self._flags

    @property
    def tags(self) -> RoleTags:
        """The tags of the role, if any."""
        return (
            RoleTags(self._tags) if self._tags
            is not None
            else RoleTags({})
        )
