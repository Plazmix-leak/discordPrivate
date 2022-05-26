import textwrap

import discord

from avocato.client.error import PlazmixApiError
from avocato.client.methods.news import PlazmixNews

from sqlalchemy import create_engine, Column, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .helpers import set_news_components

engine = create_engine("sqlite:///news-data.db", echo=True)
Base = declarative_base()


class NewsData(Base):
    __tablename__ = "news"

    id = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    post_id = Column(Integer, unique=True)
    sent = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, future=True)


class NewsScript:
    def __init__(self):
        self.session = Session()

    def write_new_posts(self) -> None:
        posts = PlazmixNews.last()
        for post in posts:
            raw_post = self.session.query(NewsData).filter(NewsData.post_id == post.id).first()
            if raw_post is not None:
                continue

            news_data = NewsData()

            news_data.post_id = post.id
            self.session.add(news_data)
            self.session.commit()

    def form_sending_list(self):
        posts = self.session.query(NewsData).all()
        to_send = []
        for post in posts:
            if post.sent is True:
                continue

            print(post.post_id)

            try:
                plazmix_post = PlazmixNews.get_from_id(int(post.post_id))
                print(plazmix_post.title)
            except PlazmixApiError:
                print("WEIRD API ERROR WHILE GETTING NEWS?")
                continue

            to_send.append(plazmix_post)

        return to_send

    def mark_as_sent(self, post):
        self.session.query(NewsData) \
            .filter(NewsData.post_id == post.id) \
            .update({
                NewsData.sent: True
            })

        self.session.commit()

    async def send_post(self, channel, post):
        embed = discord.Embed(
            title=post.title,
            description=post.full_text,
            timestamp=discord.utils.utcnow()
        )

        if post.image is not None:
            embed.set_image(url=post.image)

        embed.set_author(name=post.author, url=post.more_link)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label='Читать далее',
            url=post.more_link,
            style=discord.ButtonStyle.url
        ))

        message = await channel.send(embed=embed, view=view)

        print(message)

        await set_news_components(message, post.full_text)
        self.mark_as_sent(post)
