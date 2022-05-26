import discord


class ButtonYes(discord.ui.Button):

    """Single button"""

    def __init__(self):
        super().__init__(
            label='Да!',
            style=discord.ButtonStyle.green,
            custom_id="TICKET-YES",
            emoji='✔️'
        )

    async def callback(self, interaction):
        pass


class ButtonNo(discord.ui.Button):

    """Single button"""

    def __init__(self):
        super().__init__(
            label='Нет...',
            style=discord.ButtonStyle.red,
            custom_id="TICKET-NO",
            emoji='✖️'
        )

    async def callback(self, interaction):
        pass


class TagButtonYes(discord.ui.Button):

    """Single button"""

    def __init__(self):
        super().__init__(
            label='Добавить тег',
            style=discord.ButtonStyle.green,
            custom_id="TAG-ADD",
            emoji='✔️'
        )

    async def callback(self, interaction):
        pass


class TagButtonNo(discord.ui.Button):

    """Single button"""

    def __init__(self):
        super().__init__(
            label='Отмена',
            style=discord.ButtonStyle.gray,
            custom_id="TAG-DEL",
            emoji='❌'
        )

    async def callback(self, interaction):
        pass
