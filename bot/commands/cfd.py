import discord
from discord import app_commands
from interactions.cfd import Cfd


@app_commands.command(description="Submit a new CFD")
async def cfd(interaction: discord.Interaction):
    await interaction.response.send_modal(Cfd())
