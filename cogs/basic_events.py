# -*- coding: utf-8 -*-

import os
import textwrap

from discord.ext import commands, tasks
from components import set_news_components


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.news_channel_id = os.getenv("NEWS_CHANNEL")

    @commands.Cog.listener()
    async def on_message(self, message):

        """ NEWS """

        if message.channel.id in [
            int(self.news_channel_id),
            888161660035035136,
            882630782441627698,
            892354938317963305
        ]:
            if message.author.id == self.bot.user.id:
                return

            await set_news_components(message, message.content)

        """ OTHER """


def setup(bot):
    bot.add_cog(Events(bot))
