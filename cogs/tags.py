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
from discord.commands import Option

from components import TagButtonNo, TagButtonYes

engine = create_engine("sqlite:///tags-data.db", echo=False)
Base = declarative_base()


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    author = Column('author_id', Integer)
    name = Column('name', String, nullable=True, unique=True)
    text = Column('text', String, nullable=True)


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, future=True)


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = Session()

    @commands.slash_command(guild_ids=[int(os.getenv("PARENT_GUILD"))])
    async def tag(self, ctx, name: Option(str, "Название тега.")):
        """Отображает информацию по выбраному тегу."""  # <- yes
        statement = select(Tag).filter_by(name=name)
        result = self.session.execute(statement).all()

        if len(result) == 0:
            await ctx.respond(f"Тега с названием `{name}` не существует! :x:")
            return

        text = ""

        for r in result:
            text, author = r[0].text, r[0].author

        author = ctx.guild.get_member(author)

        author_dp = author.display_name

        if author is None:
            author_dp = "Неизвестный автор..."

        embed = discord.Embed(
            colour=discord.Colour.purple(),
            description=text
        )

        embed.set_footer(text=f"Автор: {author_dp}")

        await ctx.respond(
            embed=embed
        )

    @commands.slash_command(guild_ids=[int(os.getenv("PARENT_GUILD"))])
    @commands.has_any_role("OWNER", "Developer", "Administrator", "Discord Administrator")
    async def addtag(self, ctx, name: Option(str, "Название тега."), text: Option(str, "Текст тега.")):
        """Добавляет тег."""  # <- yes
        statement = select(Tag).filter_by(name=name)
        result = self.session.execute(statement).all()

        resmes = await ctx.respond(f"Добавляем тег **{name}** <a:loading:902256686373412926>")

        if len(result) != 0:
            await resmes.edit(f"Тега с названием `{name}` уже существует! :x:")
            return

        embed = discord.Embed(
            title=f'Добавить тег с названием "{name}"?',
            colour=discord.Colour.purple(),
            description=text
        )

        embed.set_footer(text=f"Автор: {ctx.author.display_name}")

        view = discord.ui.View()
        view.add_item(TagButtonYes())
        view.add_item(TagButtonNo())

        resmes = await ctx.respond(
            embed=embed,
            view=view
        )

        try:
            local_interaction = await self.bot.wait_for('interaction', timeout=30.0)
        except asyncio.TimeoutError:
            await resmes.edit("Время на подтверждение вышло, отмена... :x:")
            return

        else:
            custom_id = local_interaction.data.get('custom_id')
            if custom_id == "TAG-ADD":
                tag = Tag()

                tag.author = ctx.author.id
                tag.name = name
                tag.text = text
                self.session.add(tag)
                self.session.commit()

                await resmes.edit(f"Тег **{name}** успешно добавлен.", embed=None, view=None)

                return

            await resmes.edit("Добавление успешно отменено!", embed=None, view=None)


def setup(bot):
    bot.add_cog(Tags(bot))
