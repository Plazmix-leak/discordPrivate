import discord
import textwrap


async def set_news_components(message: discord.Message, content: str):
    await message.add_reaction("<:badge_legend:894341056496300122>")
    await message.add_reaction("🚀")
    await message.add_reaction("<:logo:893167676720054322>")

    string = textwrap.shorten(content, width=12, placeholder="...")

    await message.create_thread(name="Обсуждение. " + string, auto_archive_duration=1440)
