import discord
import traceback

from utils.constants import Colors


class Cfd(discord.ui.Modal, title="CFD"):
    cfd_title = discord.ui.TextInput(
        label="CFD Title",
        placeholder="Who are we defending?",
    )

    coordinates = discord.ui.TextInput(
        label="Coordinates",
        placeholder="x|y or x/y",
    )

    land_time = discord.ui.TextInput(
        label="Land Time",
        placeholder="yy/mm/dd hh:mm:ss, e.g. 23/04/20",
    )

    amount_requested = discord.ui.TextInput(
        label="Amount Requested",
        placeholder="How much defense do we need?",
    )

    notes = discord.ui.TextInput(
        label="Notes",
        style=discord.TextStyle.long,
        placeholder="Leave any other relevant information here",
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(color=Colors.SUCCESS)
        embed.add_field(name="Title", value=f"{self.cfd_title.value}", inline=False)
        embed.add_field(
            name="Coordinates", value=f"{self.coordinates.value}", inline=False
        )
        embed.add_field(name="Land Time", value=f"{self.land_time.value}", inline=False)
        embed.add_field(
            name="Defense Requested",
            value=f"{self.amount_requested.value}",
            inline=False,
        )
        embed.add_field(name="Notes", value=f"{self.notes.value}", inline=False)
        await interaction.response.send_message(
            embed=embed,
            ephemeral=False,
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )

        traceback.print_exception(type(error), error, error.__traceback__)
