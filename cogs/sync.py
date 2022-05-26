# -*- coding: utf-8 -*-

import os

import discord
from discord.ext import commands, tasks

from components import SyncScript, SyncMeView


class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = int(os.getenv("PARENT_GUILD"))
        self.log_channel_id = int(os.getenv("LOG_CHANNEL"))
        self.sync_loop_10.start()

    @commands.has_permissions(administrator=True)
    @commands.command(name='debug-SSM')
    async def debug_tool_message_sync(self, ctx):
        await ctx.send(
            embed=discord.Embed(
                title='Plazmix Network',
                colour=discord.Colour.purple(),
                description="**Синхронизация дискорд аккаунт с сервером**\n\n"
                            "Если вы хотите, синхронизировать свои группы и бейджики с сервером, то нажмите на кнопку "
                            "\"синхронизация\" под этим текстом! \n\n"
                            "**Как это работает ?**\n"
                            "`1.` Для начала, вам необходимо привязать свой дискорд аккаунт к Plazmix, для этого "
                            "перейдите [cюда (тык)](https://profile.plazmix.net/settings) и в разделе *связанные "
                            "аккаунты* привяжите __Discord__\n"
                            "`2.` Вернитесь в дискорд и нажмите кнопку \"синхронизация\"\n"
                            "`3.` Готово!\n\n"
                            "*Синхронизация работает благодаря публичным WEB API проекта, [подробнее (тык)]("
                            "https://dev.plazmix.net).* "
            ),
            view=SyncMeView()
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        script = SyncScript()
        await script.check_and_add_role(member)

    @commands.has_permissions(administrator=True)
    @commands.command(name='force-sync')
    async def forced_sync(self, ctx, member: discord.Member):
        added_roles = await SyncScript().sync_roles(member)
        print(added_roles)
        # await ctx.send(content='some', view=SyncMeView())

    @tasks.loop(minutes=10)
    async def sync_loop_10(self):
        guild = await self.bot.fetch_guild(self.guild_id)
        channel = await self.bot.fetch_channel(self.log_channel_id)
        async for member in guild.fetch_members(limit=None):
            changes = await SyncScript().sync_roles(member)
            if len(changes) != 0:
                lenght_of_changes = \
                    len(changes['plus']) + \
                    len(changes['minus']) + \
                    len(changes['plus_badges']) + \
                    len(changes['minus_badges'])
                if lenght_of_changes == 0:
                    continue
                await SyncScript().log_changes(log_data=changes, channel=channel)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        custom_id = interaction.data.get("custom_id")

        if custom_id != "SYNC-ROLES":
            return

        result = await SyncScript().check_and_add_role(interaction.user)
        if result:
            return await interaction.response.send_message(
                content="**Ваши роли успешно синхронизированы! :white_check_mark:**",
                ephemeral=True
            )

        return await interaction.response.send_message(
            content="**Упс!** Ваш аккаунт дискорда уже *синхронизирован* или не найден привязанный к нему профиль "
                    "Plazmix :weary: ",
            ephemeral=True
        )


def setup(bot):
    bot.add_cog(Sync(bot))
