# -*- coding: utf-8 -*-

import os

import discord
from discord.ext import commands, tasks
from components import NewsScript


class NewsSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.news_loop_5.start()
        self.news_channel_id = int(os.getenv("NEWS_CHANNEL"))

    @tasks.loop(minutes=1)
    async def news_loop_5(self):
        script = NewsScript()
        channel = await self.bot.fetch_channel(self.news_channel_id)

        script.write_new_posts()

        to_send = script.form_sending_list()

        for post in to_send:
            if post.author != "Plazmix Network":
                continue
            await script.send_post(channel, post)


def setup(bot):
    bot.add_cog(NewsSync(bot))
