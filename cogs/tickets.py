# -*- coding: utf-8 -*-

import asyncio
import os
import random

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from components import ButtonNo, ButtonYes, TicketCloseView, TicketOpenView

engine = create_engine("sqlite:///ticket-data.db", echo=False)
Base = declarative_base()


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    channel_id = Column('channel_id', Integer, nullable=True)
    author = Column('author_id', Integer, unique=True)
    messages = Column('messages', String, nullable=True)


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, future=True)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category_id = os.getenv("TICKETS_CATEGORY")
        self.session = Session()

    # КОМАНДА ДЛЯ ОТПРАВКИ СООБЩЕНИЯ ДЕБАГА, ЕСЛИ ЧТО-ТО СЛОМАЛОСЬ
    # ПРИМЕЧАНИЕ: СООБЩЕНИЕ ОТПРАВЛЯЕТСЯ В КАНАЛ ОТПРАВКИ КОМАНДЫ.

    @has_permissions(administrator=True)
    @commands.command(name='debug-STM')
    async def debug_stm(self, ctx):

        embed = discord.Embed(
            description="Привет, в этом канале вы можете открыть персональный **тикет**, на который ответить наш "
                        "**агент технической поддержки** и поможет решить любой ваш вопрос ! Перед открытием "
                        "убедитесь, что ответа на ваш вопрос *нету в F.A.Q.*.  *Так-же у нас есть несколько правил "
                        "для тикетов:*\n\n"
                        "- Вы можете открывать **только 1 тикет за раз**!\n"
                        "- Когда вы откроете тикет вам опишется свод правил, при их нарушении вас могу наказать!\n\n"
                        "Старайтесь описать вашу проблему максимально подробно, чтобы наши агенты могли вам помочь "
                        "как можно быстрее!\n\n"
                        "**Для открытия тикета нажмите Открыть тикет под этим сообщением!**",
            colour=discord.Colour.purple()
        )
        embed.set_author(name='Plazmix Staff Team', icon_url='https://i.imgur.com/k2A19QL.png')
        embed.set_footer(text='(c) Plazmix Staff Team')

        await ctx.send(embed=embed, view=TicketOpenView())

    # тут заканчивается дебаг

    async def send_misc_messages(self, channel: discord.TextChannel, user: discord.Member):
        await channel.send(
            content=f"{user.mention}",
            embed=discord.Embed(
                title="Plazmix Tickets",
                colour=discord.Color.purple(),
                description=f"**Привет, {user.mention}**, вы открыли персональный чат с технической поддержкой "
                            f"проекта, по нашим регламентам у вас есть 1 час для написания сообщения в этот "
                            f"канал, в противном случае наша система закроет этот тикет и вы не сможете открыть "
                            f"новый в течении 24 часов. Пожалуйста, сформулируйте свой вопрос максимально "
                            f"точно и понятно, чтобы наши агенты смогли вам помочь максимально быстро, "
                            f"так же старайтесь не использовать ненормативную лексику и не оскорбляйте "
                            f"модераторов, в противном случае нам прийдётся вас заблокировать. "
                            f"Наша система сохраняет любое сообщение написанное в данном канале "
                            f"для улучшения качества работы отдела технической поддержки!\n\n"

                            "*Если вы открыли тикет случайно, то нажмите кнопку под этим сообщением. "
                            "Так-же советуем вам ознакомится с разделом F.A.Q. возможно там вы сможете "
                            "найти ответ на интересующий вас вопрос.*\n\n"

                            "!! *Важное замечание: вы можете открывать только 1 тикет в час* !!\n\n"

                            "**Написав сообщения в этот канал, вы соглашаетесь с нашей политикой обработки "
                            "персональных данных!**"
            ),
            view=TicketCloseView()
        )

    async def create_ticket_channel(self, user: discord.Member, guild) -> discord.TextChannel:
        category = await self.bot.fetch_channel(self.category_id)
        ticket = Ticket()

        ticket.author = user.id
        self.session.add(ticket)
        self.session.commit()

        channel = await category.create_text_channel(f"📚тикет-{ticket.id}")

        await channel.set_permissions(user, send_messages=True, view_channel=True)

        ticket.channel_id = channel.id
        self.session.commit()

        await self.send_misc_messages(channel=channel, user=user)

        return channel

    async def open_ticket(self, user, interaction) -> str:
        try:
            channel = await self.create_ticket_channel(user=user, guild=interaction.guild)
            return f"**Ваш тикет успешно создан в канале -> {channel.mention}**"
        except IntegrityError:
            self.session.rollback()
            return f"**У вас уже есть открытый тикет!**\n*Если вы считаете это ошибкой, обратитесь в службу поддержки по" \
                   f"ссылке -> <https://vk.com/plazmixdevs>*"
        except Exception as e:
            return f"**Не удалось создать тикет, обратитесь в поддержку по ссылке -> <https://vk.com/plazmixdevs>**\n" \
                   f"*Текст ошибки: `{e}`*"

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
    async def on_interaction(self, interaction):

        custom_id = interaction.data.get("custom_id")

        if custom_id == "TICKET-CLOSE":
            channel = interaction.channel
            statement = select(Ticket).filter_by(channel_id=channel.id)
            result = self.session.execute(statement).all()
            if len(result) == 0:
                return

            channel_id, author_id = 0, 0

            for r in result:
                channel_id, author_id = r[0].channel_id, r[0].author

            view = discord.ui.View()
            view.add_item(ButtonYes())
            view.add_item(ButtonNo())

            local_message = await interaction.channel.send(
                embed=discord.Embed(
                    title="Вы уверены?",
                    description="Вы уверены, что хотите удалить этот тикет?",
                    colour=discord.Colour.purple()
                ),
                view=view
            )

            try:
                local_interaction = await self.bot.wait_for('interaction', timeout=30.0)
            except asyncio.TimeoutError:
                await local_message.delete()
                temp_message = await interaction.channel.send(
                    content=":x: Время вышло..."
                )

                await asyncio.sleep(5)

                await temp_message.delete()

            else:

                local_custom_id = local_interaction.data.get('custom_id')

                if local_custom_id == "TICKET-YES":
                    message = await self.delete_ticket(interaction=interaction, channel_id=channel_id,
                                                       author=author_id)
                    if message is not None:
                        return
                    await local_interaction.response.defer(ephemeral=True)
                elif local_custom_id == "TICKET-NO":
                    await local_interaction.message.delete()
                else:
                    pass

            # TODO: Доделать авто-удаление.

        if not custom_id == "TICKET-OPEN":
            return

        content = await self.open_ticket(user=interaction.user, interaction=interaction)

        await interaction.response.send_message(ephemeral=True, content=content)


def setup(bot):
    bot.add_cog(Tickets(bot))
