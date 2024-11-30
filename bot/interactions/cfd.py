import discord
import traceback

from utils.constants import Colors
from utils.config_manager import read_config_str


class Cfd(discord.ui.Modal, title="CFD"):
    cfd_title = discord.ui.TextInput(
        label="CFD Title",
        placeholder="Who are we defending?",
        required=True,
    )

    x_coordinate = discord.ui.TextInput(
        label="X-Coordinate",
        placeholder="X",
        required=True,
    )

    y_coordinate = discord.ui.TextInput(
        label="Y-Coordinate",
        placeholder="Y",
        required=True,
    )

    land_time = discord.ui.TextInput(
        label="Land Time",
        placeholder="yy/mm/dd hh:mm:ss, e.g. 23/04/20",
        required=True,
    )

    amount_requested = discord.ui.TextInput(
        label="Amount Requested",
        placeholder="How much defense do we need?",
        required=True,
    )

    # notes = discord.ui.TextInput(
    #     label="Notes",
    #     style=discord.TextStyle.long,
    #     placeholder="Leave any other relevant information here",
    #     required=False,
    # )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(color=Colors.SUCCESS)
        embed.add_field(name="Title", value=f"{self.cfd_title.value}", inline=False)
        # Get the game server URL using the guild ID as the section
        guild_id = str(interaction.guild_id)
        game_server = read_config_str(guild_id, "game_server", "")
        
        # Create coordinate field with link if game server is configured
        if game_server:
            coord_link = f"[({self.x_coordinate.value}|{self.y_coordinate.value})]({game_server}/position_details.php?x={self.x_coordinate.value}&y={self.y_coordinate.value})"
            embed.add_field(name="Coordinates", value=coord_link, inline=False)
        else:
            embed.add_field(name="Coordinates", value=f"({self.x_coordinate.value}|{self.y_coordinate.value})", inline=False)
        
        embed.add_field(name="Land Time", value=f"{self.land_time.value}", inline=False)
        embed.add_field(
            name="Defense Requested",
            value=f"{self.amount_requested.value}",
            inline=False,
        )
        # embed.add_field(name="Notes", value=f"{self.notes.value}", inline=False)
        
        # Get the role by name
        role = discord.utils.get(interaction.guild.roles, name="Dev")
        
        # Send the initial response
        if role:
            await interaction.response.send_message(
                content=f"{role.mention} New CFD Request!",
                embed=embed,
                ephemeral=False,
            )
        else:
            await interaction.response.send_message(
                content="New CFD Request! (Could not find role to mention)",
                embed=embed,
                ephemeral=False,
            )
        
        # Get the message object from the original interaction
        original_message = await interaction.original_response()
        
        # Get the game server URL using the guild ID as the section
        guild_id = str(interaction.guild_id)
        game_server = read_config_str(guild_id, "game_server", "")
        
        if game_server:
            coord_link = f"[({self.x_coordinate.value}|{self.y_coordinate.value})]({game_server}/position_details.php?x={self.x_coordinate.value}&y={self.y_coordinate.value})"
            thread_message = f"Please use this thread to coordinate the defense effort for coordinates {coord_link}!"
        else:
            thread_message = f"Please use this thread to coordinate the defense effort for coordinates ({self.x_coordinate.value}|{self.y_coordinate.value})!"
        
        # Create a thread from the message
        thread_name = f"CFD: {self.cfd_title.value}"
        thread = await original_message.create_thread(name=thread_name)
        
        # Send a message in the thread
        await thread.send(thread_message)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )

        traceback.print_exception(type(error), error, error.__traceback__)
