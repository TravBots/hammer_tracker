import discord
from discord import app_commands
from discord.ext import tasks
import configparser
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from utils.constants import crop_production
from utils.errors import *
from funcs import *
from utils.hero import *
from utils.validators import *

from factory import AppFactory

from interactions.cfd import Cfd

intents = discord.Intents.all()
intents.message_content = True


class Core(discord.Client):
    def __init__(
        self,
        *,
        intents: discord.Intents,
        **options: Any,
    ) -> None:
        super().__init__(intents=intents, **options)
        self.tree = app_commands.CommandTree(self)
        self.config: configparser.ConfigParser = configparser.ConfigParser()
        self.config.read("config.ini")

        self.token = self.config["default"]["token"]

        self.factory = AppFactory()

    async def setup_hook(self):
        self.close_threads.start()

        await self.tree.sync()

    async def on_message(self, message: discord.Message):
        # Does mixing async with sync code like this mess anything up?
        app = self.factory.return_app(message)
        if app is not None:
            await app.run()

        if coordinates_are_valid(message.content):
            if not message.author.bot:
                slash = "/" in message.content
                pipe = "|" in message.content

                if slash:
                    xy = message.content.split("/")
                elif pipe:
                    xy = message.content.split("|")
                x = xy[0].strip()
                y = xy[1].strip()
                game_server = self.config[str(message.guild.id)]["game_server"]
                embed = discord.Embed(color=Colors.SUCCESS)
                embed.add_field(
                    name="",
                    value=f"{game_server}/position_details.php?x={x}&y={y}",
                )
                await message.channel.send(embed=embed)

    async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
        # Refresh config
        self.config.read("config.ini")
        guild_id = str(event.guild.id)
        defense_channel = self.config[guild_id]["defense_channel"]
        game_server = self.config[guild_id]["game_server"]

        x, y = event.location.replace("/", "|").split("|")

        cfd_id = create_cfd(
            db_name=f"databases/{guild_id}.db",
            created_by_id=event.creator.id,
            event_id=event.id,
            created_by_name=event.creator.display_name,
            land_time=event.start_time,
            x_coordinate=x,
            y_coordinate=y,
            amount_requested=event.description,
        )
        embed = discord.Embed(color=Colors.SUCCESS)
        map_link = f"[{x}|{y}]({game_server}/position_details.php?x={x}&y={y})"
        land_time = event.start_time.astimezone(ZoneInfo("US/Eastern"))
        message = f"""
        ID: {cfd_id}
        Submitted by: {event.creator.display_name}
        Coordinates: {map_link}
        Land Time: {str(land_time).split(".")[0]}
        Defense Required: {int(event.description):,}
            """
        embed.add_field(name=f"New CFD: {event.name}", value=message)

        channel = get_channel_from_id(event.guild, defense_channel)
        cfd_message = await channel.send(embed=embed)
        thread = await channel.create_thread(name=event.name, message=cfd_message)

        insert_defense_thread(
            db_name=f"databases/{guild_id}.db",
            defense_thread_id=thread.id,
            cfd_id=cfd_id,
            name=thread.name,
            jump_url=thread.jump_url,
        )

        await thread.send(
            content="Respond to this CFD in the thread below :point_down:"
        )

    async def on_scheduled_event_delete(self, event):
        # Refresh config
        self.config.read("config.ini")
        guild_id = str(event.guild.id)
        cancel_cfd(f"databases/{guild_id}.db", event.id)

    async def on_scheduled_event_update(self, before, after):
        """
        End events after they start
        """
        print(before.status)
        print(after.status)
        if after.status == discord.EventStatus.active:
            await after.end()

    @tasks.loop(minutes=10.0)
    async def close_threads(self):
        # Get defense discord.Channel from config channel
        # Get threads in Channel
        # For each thread, get associated cfd
        # If cfd land_time is in the past, archive the thread
        for guild in client.guilds:
            try:
                if self.config[str(guild.id)]["clean_up_threads"].lower() == "true":
                    channel = get_channel_from_id(
                        guild, self.config[str(guild.id)]["defense_channel"]
                    )

                    if len(channel.threads) == 0:
                        continue

                    print(f"Cleaning up threads for {guild}")
                    conn = sqlite3.connect(f"databases/{guild.id}.db")
                    for thread in channel.threads:
                        query = """
                        select 
                            dc.land_time 
                        from defense_threads dt 
                        join defense_calls dc 
                            on dt.defense_call_id = dc.id 
                        where dt.id = ?;"""
                        # fmt: off
                        data = (str(thread.id),)
                        # fmt: on
                        rows = conn.execute(query, data)
                        cfd_thread = rows.fetchone()
                        if cfd_thread is None:
                            continue

                        land_time = datetime.strptime(
                            cfd_thread[0].split(".")[0], "%Y-%m-%d %H:%M:%S"
                        )
                        if land_time < datetime.utcnow():
                            print(f"Archiving thread {thread.name}")
                            await thread.edit(archived=True)
            except KeyError:
                print(f"Failed to clean up threads for {guild}")


if __name__ == "__main__":
    client = Core(intents=intents)

    @client.tree.command()
    @app_commands.choices(
        cropper_type=[
            app_commands.Choice(name="6 Crop", value=6),
            app_commands.Choice(name="7 Crop", value=7),
            app_commands.Choice(name="9 Crop", value=9),
            app_commands.Choice(name="15 Crop", value=15),
        ]
    )
    @app_commands.choices(
        gold_bonus=[
            app_commands.Choice(name="Yes", value=0.0),
            app_commands.Choice(name="No", value=0.25),
        ]
    )
    @app_commands.choices(
        oasis_bonus=[
            app_commands.Choice(name="0%", value=0.0),
            app_commands.Choice(name="25%", value=0.25),
            app_commands.Choice(name="50%", value=0.50),
            app_commands.Choice(name="75%", value=0.75),
            app_commands.Choice(name="100%", value=1.00),
            app_commands.Choice(name="125%", value=1.25),
            app_commands.Choice(name="150%", value=1.50),
        ]
    )
    @app_commands.choices(
        flour_mill_bakery=[
            app_commands.Choice(name="5%", value=0.05),
            app_commands.Choice(name="10%", value=0.10),
            app_commands.Choice(name="15%", value=0.15),
            app_commands.Choice(name="20%", value=0.20),
            app_commands.Choice(name="25%", value=0.25),
            app_commands.Choice(name="30%", value=0.30),
            app_commands.Choice(name="35%", value=0.35),
            app_commands.Choice(name="40%", value=0.40),
            app_commands.Choice(name="45%", value=0.45),
            app_commands.Choice(name="50%", value=0.50),
        ]
    )
    @app_commands.choices(
        field_levels=[
            app_commands.Choice(name="10", value=10),
            app_commands.Choice(name="11", value=11),
            app_commands.Choice(name="12", value=12),
            app_commands.Choice(name="13", value=13),
            app_commands.Choice(name="14", value=14),
            app_commands.Choice(name="15", value=15),
            app_commands.Choice(name="16", value=16),
            app_commands.Choice(name="17", value=17),
            app_commands.Choice(name="18", value=18),
            app_commands.Choice(name="19", value=19),
            app_commands.Choice(name="20", value=20),
        ]
    )
    @app_commands.describe(
        crop_1="Amount of crop scouted in first report",
        crop_2="Amount of crop scouted in second report",
        seconds_between_scoutings="The number of seconds between the first and second scout report",
        cropper_type="Crop type of village",
        field_levels="Level of crop fields in the village",
        oasis_bonus="Crop bonus from oases",
        reins_in_village="Wheat count of all troops present in target village",
        population="Population of the target village",
        flour_mill_bakery="Crop bonus from flour mill and bakery. Default: 50%",
        gold_bonus="Does the defender have the gold bonus activated? Default: Yes",
    )
    async def scout(
        interaction: discord.Interaction,
        crop_1: int,
        crop_2: int,
        seconds_between_scoutings: int,
        field_levels: int,
        oasis_bonus: float,
        reins_in_village: int,
        population: int,
        cropper_type: int,
        flour_mill_bakery: float = 0.50,
        gold_bonus: float = 0.25,
    ):
        """Calculate a crop scout"""

        base_production = crop_production[field_levels] * cropper_type
        with_oases_mill_bakery = (
            (base_production * oasis_bonus)
            + (base_production * flour_mill_bakery)
            + base_production
        )
        with_gold_bonus = with_oases_mill_bakery * (1 + gold_bonus)
        hammer_size = (
            (((crop_1 - crop_2) / seconds_between_scoutings) * 3600)
            - reins_in_village
            + with_gold_bonus
            - population
        )

        embed = discord.Embed(color=Colors.SUCCESS)
        embed.add_field(
            name="Crop Scout Result",
            value=f"Expected hammer size (in crop consumption): **{int(hammer_size):,}**",
        )
        await interaction.response.send_message(embed=embed)

    @client.tree.command(description="Submit a new CFD")
    async def cfd(interaction: discord.Interaction):
        await interaction.response.send_modal(Cfd())

    client.run(client.token)
