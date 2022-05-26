# -*- coding: utf-8 -*-

import datetime

import aiohttp
import discord
from discord import Webhook
from discord.ext import commands


async def webhook_send(embed, url, name):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session=session)
        await webhook.send(embed=embed, username=name)


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_url = "https://canary.discord.com/api/webhooks/898334508548513812/Gg_ePOcb7zeESzdIOzmetnuFNIr" \
                           "XL6XfXyErfNnRkqZ6hdR1qA_auqvZRG_4QPFGHm-r"
        self.pass_image = "https://i.imgur.com/zon5poe.png"

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        embed = discord.Embed(colour=discord.Colour.blurple(),
                              description=f"Обновление участника {after.mention}`({after.name}"
                                          f"#{after.discriminator})`:",
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Обновление участника",
                         icon_url="https://media.discordapp.net/attachments/440559813769035796/"
                                  "760903536267100170/user_update.png")
        embed.set_footer(text=f"ID: {after.id}")
        if before.nick != after.nick:
            embed.add_field(name="Обновление никнейма",
                            value=f"`{before.nick}` -> `{after.nick}`"
                            )
        if before.roles != after.roles:
            updates_minus = ""
            updates_plus = ""
            after_roles = after.roles
            for b_role in before.roles:
                if b_role in after_roles:
                    after_roles.remove(b_role)
                else:
                    updates_minus += f"\n<:minus:894351826839810109> `{b_role.name}`;"
            for new_role in after_roles:
                updates_plus += f"\n<:plus:894351815930417202> `{new_role.name}`;"
            embed.add_field(name="Обновление ролей", value=f"{updates_plus}{updates_minus}"[:-1] + ".")
        if before.status != after.status:
            embed.add_field(name="Обновление статуса",
                            value=f"`{before.status}` -> `{after.status}`")
        if before.activity != after.activity:
            embed.add_field(name="Обновление статуса",
                            value=f"`{before.activity}` -> `{after.activity}`")

        if len(embed.fields) == 0:
            return

        embed.set_image(url=self.pass_image)

        await webhook_send(embed=embed,
                           url=self.webhook_url,
                           name='PLAZMIX LOGS | Обновление участника')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel and before.channel is None:
            embed = discord.Embed(colour=discord.Colour.green(),
                                  description=f"Участник {member.mention}`({member.name}#{member.discriminator})`"
                                              f" зашел в канал:",
                                  timestamp=datetime.datetime.utcnow())
            embed.set_author(name="Участник зашел в канал")
            embed.set_footer(text=f"ID: {member.id}")
            embed.add_field(name='Канал', value=f"<#{after.channel.id}>")
        elif before.channel != after.channel and after.channel is None:
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description=f"Участник {member.mention}`({member.name}#{member.discriminator})` "
                                              f"вышел из канала:",
                                  timestamp=datetime.datetime.utcnow())
            embed.set_author(name="Участник вышел из канала")
            embed.set_footer(text=f"ID: {member.id}")
            embed.add_field(name='Канал', value=f"<#{before.channel.id}>")
        elif before.channel != after.channel:
            embed = discord.Embed(colour=discord.Colour.gold(),
                                  description=f"Участник {member.mention}`({member.name}#{member.discriminator})` "
                                              f"перешел в другой канал:",
                                  timestamp=datetime.datetime.utcnow())
            embed.set_author(name="Участник перешел в другой канал")
            embed.set_footer(text=f"ID: {member.id}")
            embed.add_field(name='Предыдущий канал', value=f"<#{before.channel.id}>")
            embed.add_field(name='Канал', value=f"<#{after.channel.id}>")
        else:
            return

        embed.set_image(url=self.pass_image)

        await webhook_send(embed=embed,
                           url=self.webhook_url,
                           name='PLAZMIX LOGS | Обновление канала участника')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(colour=discord.Colour.green(),
                              description=f"Участник {member.mention}`({member.name}#{member.discriminator})` "
                                          f"зашел на сервер.",
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name="+Участник",
                         icon_url="https://media.discordapp.net/attachments/440559813769035796/"
                                  "760956453162188810/member_add.png")
        embed.set_footer(text=f"ID: {member.id}")
        embed.add_field(name='Зашел', value=f"{member.joined_at}"[:-13])
        embed.add_field(name='Создал аккаунт', value=f"{member.created_at}"[:-13])

        embed.set_image(url=self.pass_image)

        await webhook_send(embed=embed,
                           url=self.webhook_url,
                           name='PLAZMIX LOGS | Участник зашел')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(colour=discord.Colour.red(),
                              description=f"Участник {member.mention}`({member.name}#{member.discriminator})` "
                                          f"вышел с сервера.",
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name="-Участник",
                         icon_url="https://media.discordapp.net/attachments/720281456856924220/"
                                  "760970798927839232/member_remove.png")
        embed.set_footer(text=f"ID: {member.id}")
        embed.add_field(name='Вышел', value=f"{discord.utils.utcnow()}"[:-13])
        delta = discord.utils.utcnow() - member.joined_at
        embed.add_field(name='Пробыл на сервере', value=f"{delta.days} дн.")

        embed.set_image(url=self.pass_image)

        await webhook_send(embed=embed,
                           url=self.webhook_url,
                           name='PLAZMIX LOGS | Участник вышел')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if len(message.content) == 0: return
        embed = discord.Embed(colour=discord.Colour.red(),
                              description=f"[Ссылка]({message.jump_url})\n"
                                          f"**Автор**: {message.author.mention}`({message.author.name}#"
                                          f"{message.author.discriminator})`\n"
                                          f"**Канал**: <#{message.channel.id}> `{message.channel.name}`",
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Сообщение удалено",
                         icon_url="https://images-ext-1.discordapp.net/external/_tROiSIcg4O6vlWtB6YqWXn_YcGyo3Pw3YdzTFv"
                                  "_J3E/https/media.discordapp.net/attachments/506838906872922145/603642595419357190/"
                                  "messagedelete.png")
        embed.set_footer(text=f"ID: {message.id}")
        embed.add_field(name='Сообщение', value=f"> {message.content}")

        embed.set_image(url=self.pass_image)

        await webhook_send(embed=embed,
                           url=self.webhook_url,
                           name='PLAZMIX LOGS | Сообщение удалено')

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        embed = discord.Embed(colour=discord.Colour.red(),
                              description=f"[Ссылка]({after.jump_url})\n"
                                          f"**Автор**: {after.author.mention}`({after.author.name}#"
                                          f"{after.author.discriminator})`\n "
                                          f"**Канал**: <#{after.channel.id}> `{after.channel.name}`",
                              timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Сообщение изменено",
                         icon_url="https://images-ext-2.discordapp.net/external/pVfMiU0wuagNZVVIeAh7jOORX56xD6D"
                                  "_M9uf2oA0EQs/https/media.discordapp.net/attachments/506838906872922145/"
                                  "603643138854354944/messageupdate.png")
        embed.set_footer(text=f"ID: {after.id}")
        embed.add_field(name='До', value=f"> {before.content}")
        embed.add_field(name='После', value=f"> {after.content}")

        embed.set_image(url=self.pass_image)

        await webhook_send(embed=embed,
                           url=self.webhook_url,
                           name='PLAZMIX LOGS | Сообщение изменено')

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.attachments) == 0: return
        embed = discord.Embed(title=f"{message.attachments[0].filename}", colour=discord.Colour.blurple(),
                              description=f"**Автор**: {message.author.mention}`({message.author.name}#"
                                          f"{message.author.discriminator})`\n"
                                          f"[Ссылка на сообщение]({message.jump_url})",
                              timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Нет картинки? Файл не поддерживается.")
        att = ""
        for attach in message.attachments:
            att += f"\n[Тык]({attach.url})"
        embed.add_field(name='Вложения:', value=att)
        try:
            embed.set_image(url=message.attachments[0].url)
        except:
            embed.set_image(url=self.pass_image)
        await webhook_send(embed=embed,
                           url=self.webhook_url,
                           name='PLAZMIX LOGS | Файл в сообщении')
        await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(Logs(bot))
