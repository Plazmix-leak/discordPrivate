# -*- coding: utf-8 -*-

import asyncio
import os
import random

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord_components import Button, ButtonStyle
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///zayavka-data.db", echo=False)
Base = declarative_base()


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    channel_id = Column('channel_id', Integer, nullable=True)
    author = Column('author_id', Integer, unique=True)
    messages = Column('messages', String, nullable=True)


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, future=True)


class TicketsZ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category_id = os.getenv("ZAYAVKA_CATEGORY")
        self.session = Session()

    # КОМАНДА ДЛЯ ОТПРАВКИ СООБЩЕНИЯ ДЕБАГА, ЕСЛИ ЧТО-ТО СЛОМАЛОСЬ
    # ПРИМЕЧАНИЕ: СООБЩЕНИЕ ОТПРАВЛЯЕТСЯ В КАНАЛ ОТПРАВКИ КОМАНДЫ.

    @has_permissions(administrator=True)
    @commands.command(name='debug-STM-D')
    async def debug_stm(self, ctx):

        embed = discord.Embed(
            description="**Для открытия заявки нажмите на кнопку `Открыть заявку` ниже!**\n\n"
                        "- Вы можете создават только 1 заявку за раз!\n",
            colour=discord.Colour.blurple()
        )
        embed.set_author(name='Plazmix', icon_url='https://i.imgur.com/k2A19QL.png')
        embed.set_footer(text='(c) Plazmix Staff Team')

        await ctx.send(
            embed=embed,
            components=[[
                Button(
                    label='Открыть заявку',
                    emoji="📓",
                    custom_id="ZAYAVKA-OPEN",
                    style=ButtonStyle.gray,
                )
            ]]
        )

    # тут заканчивается дебаг

    async def send_misc_messages(self, channel: discord.TextChannel, user: discord.Member):
        await channel.send(
            content=f"{user.mention}",
            embed=discord.Embed(
                title="Plazmix Tickets",
                colour=discord.Color.blurple(),
                description=f"**Привет, {user.mention}!** Мы очень рады что ты заинтересован в должности дискорд "
                            f"модератора, "
                            f"её основания задача контролировать чат/голсовые каналы в дискорде и быть готовым помочь "
                            f"нашим замечательным игрокам, чуть вы найдёте форму заявки: \n\n"
                            f"```1. Ваше имя\n"
                            f"2. Ваша фамилия\n"
                            f"3. Ваш возраст\n"
                            f"4. Расскажите о себе, ваши хобби, чем занимаетесь ещё```\n\n"

                            f"В таком формате напишите сообщение в этот чат, администратор рассмотрим вашу заявку и "
                            f"даст вердикт сюда-же в течении 24 часов.\n\n*Если по истечению этого времени ответа не "
                            f"поступило, откройте **Тикет** в канале <#889969319411351574>*"
            ),
            components=[
                Button(
                    label='Закрыть заявку',
                    custom_id="ZAYAVKA-CLOSE",
                    emoji="🔒",
                    style=ButtonStyle.red
                )
            ]
        )

    async def create_ticket_channel(self, user: discord.Member, guild) -> discord.TextChannel:
        category = await self.bot.fetch_channel(self.category_id)
        ticket = Ticket()

        ticket.author = user.id
        self.session.add(ticket)
        self.session.commit()

        channel = await category.create_text_channel(f"📓заявка-{ticket.id}")

        await channel.set_permissions(user, send_messages=True, view_channel=True)

        ticket.channel_id = channel.id
        self.session.commit()

        await self.send_misc_messages(channel=channel, user=user)

        return channel

    async def open_ticket(self, user, interaction) -> str:
        try:
            channel = await self.create_ticket_channel(user=user, guild=interaction.guild)
            return f"**Ваша заявка успешно создан в канале -> {channel.mention}**"
        except IntegrityError:
            self.session.rollback()
            return f"**У вас уже есть открытая заявка!**\n*Если вы считаете это ошибкой, обратитесь в службу " \
                   f"поддержки по ссылке -> <https://vk.com/plazmixdevs>*"
        except Exception as e:
            return f"**Не удалось создать заявку, обратитесь в поддержку по ссылке -> <https://vk.com/plazmixdevs>**" \
                   f"\n*Текст ошибки: `{e}`*"

    async def delete_ticket(self, interaction, channel_id, author) -> str or None:
        def transform(message):
            dt = message.created_at
            time = dt.strftime('%H:%M:%S')
            hours = int(time[:2]) + 3
            formatted = str(hours) + str(time[2:])

            return f"{formatted} | {message.author.name} ({message.author.id}): {message.content}"

        iterator = interaction.channel.history().map(transform)
        print(iterator)
        messages = await iterator.flatten()
        messages.reverse()

        self.session.query(Ticket) \
            .filter(Ticket.channel_id == channel_id) \
            .update({
            Ticket.author: str(author) + f".old.{random.randint(0, 99999)}",
            Ticket.messages: str(messages)
        })

        self.session.commit()

        await interaction.channel.delete(reason=f'Тикет "{interaction.channel.name}" '
                                                f'закрыт пользователем {interaction.user.name}'
                                                f', ID Автора: {author}')
        return None

    @commands.Cog.listener()
    async def on_button_click(self, interaction):

        if interaction.component.custom_id == "ZAYAVKA-CLOSE":
            channel = interaction.channel
            statement = select(Ticket).filter_by(channel_id=channel.id)
            result = self.session.execute(statement).all()
            if len(result) == 0:
                return

            channel_id, author_id = 0, 0

            for r in result:
                channel_id, author_id = r[0].channel_id, r[0].author

            await interaction.respond(type=6)
            local_message = await interaction.channel.send(
                embed=discord.Embed(
                    title="Вы уверены?",
                    description="Вы уверены, что хотите удалить эту заявку?",
                    colour=discord.Colour.blurple()
                ),
                components=[[
                    Button(
                        label="Да!",
                        emoji="✅",
                        custom_id="ZAYAVKA-YES",
                        style=ButtonStyle.gray
                    ),
                    Button(
                        label="Нет...",
                        emoji="❌",
                        custom_id="ZAYAVKA-NO",
                        style=ButtonStyle.gray
                    )
                ]]
            )

            try:
                local_interaction = await self.bot.wait_for('button_click', timeout=30.0)
            except asyncio.TimeoutError:
                await local_message.delete()
                temp_message = await interaction.channel.send(
                    content=":x: Время вышло..."
                )

                await asyncio.sleep(5)

                await temp_message.delete()

            else:
                if local_interaction.component.custom_id == "ZAYAVKA-YES":
                    message = await self.delete_ticket(interaction=interaction, channel_id=channel_id,
                                                       author=author_id)
                    if message is not None:
                        await local_interaction.respond(type=4, ephemeral=True, content=message)
                        return
                    await local_interaction.respond(type=6)
                elif local_interaction.component.custom_id == "ZAYAVKA-NO":
                    await local_interaction.respond(type=6)
                    await local_interaction.message.delete()
                else:
                    pass

            # TODO: Доделать авто-удаление.

        if not interaction.component.custom_id == "ZAYAVKA-OPEN":
            return

        content = await self.open_ticket(user=interaction.user, interaction=interaction)

        await interaction.respond(type=4, content=content)


def setup(bot):
    bot.add_cog(TicketsZ(bot))
