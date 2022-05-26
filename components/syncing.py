import os

import discord

from avocato.client.error import PlazmixApiError
from avocato.client.methods.user import PlazmixUser
from .group_to_discord import GroupCollection, BadgeCollection


class SyncScript:
    def __init__(self):
        self.blocking_role_id = os.getenv("BLOCKING_ROLE")
        self.sync_role_id = os.getenv("SYNC_ROLE")

    async def check_and_add_role(self, user: discord.Member) -> bool:
        try:
            PlazmixUser.get_from_discord_id(user.id)
        except PlazmixApiError:
            return False

        role = user.guild.get_role(int(self.sync_role_id))

        if role in user.roles:
            return False

        await user.add_roles(role)
        await self.sync_roles(user)
        return True

    def check_blocking_roles(self, user: discord.Member) -> bool:
        role = user.guild.get_role(int(self.blocking_role_id))
        second_role = user.guild.get_role(int(self.sync_role_id))

        if second_role not in user.roles:
            return True

        if role in user.roles:
            return True

        return False

    async def log_changes(self, log_data: dict[str, set], channel: discord.TextChannel) -> discord.Message:
        plus_string = ""
        minus_string = ""
        plus_badge_string = ""
        minus_badge_string = ""

        for plus_role in log_data['plus']:
            plus_string += f"➕ <@&{plus_role.value.discord_role_id}>\n"

        for plus_badge in log_data['plus_badges']:
            plus_badge_string += f"➕ <@&{plus_badge.value.discord_role_id}>\n"

        for minus_role in log_data['minus']:
            minus_string += f"➖ <@&{minus_role.value.discord_role_id}>\n"

        for minus_badge in log_data['minus_badges']:
            minus_badge_string += f"➖ <@&{minus_badge.value.discord_role_id}>\n"

        embed = discord.Embed(
            title='Изменение ролей',
            colour=discord.Colour.green(),
            description=f"Изменение ролей для <@{log_data['user']}>\n\n"
                        f"**Добавлены:**\n"
                        f"{plus_string}"
                        f"{plus_badge_string}"
                        f"\n\n"
                        f"**Убраны:**\n"
                        f"{minus_string}"
                        f"{minus_badge_string}"
        )

        return await channel.send(embed=embed)

    async def sync_roles(self, user: discord.Member) -> dict[str, set or int]:
        if self.check_blocking_roles(user):
            return {}

        try:
            plazmix_user = PlazmixUser.get_from_discord_id(user.id)
        except PlazmixApiError:
            return {}

        server_roles = plazmix_user.all_permission_group
        badges = plazmix_user.badges

        guild_valid_roles = []
        guild_valid_badges = []

        for server_role in server_roles:
            try:
                guild_valid_roles.append(GroupCollection.get_from_plazmix_group(server_role))
            except ValueError:
                continue

        for badge in badges:
            try:
                guild_valid_badges.append(BadgeCollection.get_from_technical_name(badge.technical_name))
            except ValueError:
                continue

        discord_guild_roles = user.roles
        guild_roles = []

        guild_badges = []

        for discord_guild_role in discord_guild_roles:
            try:
                guild_badges.append(BadgeCollection.get_from_discord_id(discord_guild_role.id))
            except ValueError:
                pass

            try:
                guild_roles.append(GroupCollection.get_from_discord_id(discord_guild_role.id))
            except ValueError:
                continue

        donator_roles = [
            GroupCollection.STAR.value,
            GroupCollection.COSMO.value,
            GroupCollection.GALAXY.value,
            GroupCollection.UNIVERSE.value,
            GroupCollection.LUXURY.value
        ]

        guild_valid_roles = set(guild_valid_roles)
        guild_valid_badges = set(guild_valid_badges)
        guild_roles = set(guild_roles)
        guild_badges = set(guild_badges)

        minus_groups = guild_roles - guild_valid_roles
        plus_groups = guild_valid_roles - guild_roles

        minus_badges = guild_badges - guild_valid_badges
        plus_badges = guild_valid_badges - guild_badges

        for minus_group in minus_groups:
            if minus_group.value in donator_roles:
                sub_role = user.guild.get_role(893617672045088788)
                await user.remove_roles(sub_role)
            discord_role = user.guild.get_role(minus_group.value.discord_role_id)
            await user.remove_roles(discord_role)

        for plus_group in plus_groups:
            if plus_group.value in set(donator_roles):
                sub_role = user.guild.get_role(893617672045088788)
                await user.add_roles(sub_role)
            discord_role = user.guild.get_role(plus_group.value.discord_role_id)
            await user.add_roles(discord_role)

        for minus_badge in minus_badges:
            discord_role = user.guild.get_role(minus_badge.value.discord_role_id)
            await user.remove_roles(discord_role)

        for plus_badge in plus_badges:
            discord_role = user.guild.get_role(plus_badge.value.discord_role_id)
            await user.add_roles(discord_role)

        return {
            "user": user.id,
            "plus": plus_groups,
            "minus": minus_groups,
            "plus_badges": plus_badges,
            "minus_badges": minus_badges
        }
