import time

from dotenv import load_dotenv
load_dotenv()

import os
import discord
from discord.ext import commands
#from discord_components import ComponentsBot


def main():
    intents = discord.Intents(
        guilds=True,
        members=True,
        bans=True,
        emojis=True,
        voice_states=True,
        messages=True,
        reactions=True,
    )

    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=None
    )

    # Loading bunch of cogs
    bot.load_extension("cogs.basic_events"), print("events loaded")
    bot.load_extension("cogs.logs"), print("logs loaded")
    bot.load_extension("cogs.tickets"), print("tickets loaded")
    bot.load_extension("cogs.sync"), print("sync loaded")
    bot.load_extension("cogs.news"), print("news loaded")
    bot.load_extension("cogs.tags"), print("tags loaded")

    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    main()

