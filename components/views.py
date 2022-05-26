import discord
from .buttons import *
from .syncing import SyncScript


class TicketOpenView(discord.ui.View):
    """Single button view"""

    @discord.ui.button(
        label='Открыть тикет',
        style=discord.ButtonStyle.gray,
        custom_id="TICKET-OPEN"
    )
    async def button_callback(self, button, interaction):
        pass


class TicketCloseView(discord.ui.View):
    """Single button view"""

    @discord.ui.button(
        label='Закрыть тикет',
        style=discord.ButtonStyle.red,
        custom_id="TICKET-CLOSE",
        emoji='🔒'
    )
    async def button_callback(self, button, interaction):
        pass


class SyncMeView(discord.ui.View):
    """Single button view"""

    @discord.ui.button(
        label='Синхронизировать',
        style=discord.ButtonStyle.gray,
        custom_id="SYNC-ROLES",
        emoji='⚙️'
    )
    async def button_callback(self, button, interaction):
        pass
