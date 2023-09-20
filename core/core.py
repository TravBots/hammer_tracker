import discord
import configparser
from typing import Any

from errors import *
from funcs import *
from hero import *
from validators import *

from factory import AppFactory

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
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.token = self.config["default"]["token"]

        self.factory = AppFactory()

    async def on_message(self, message):
        # Does mixing async with sync code like this mess anything up?
        app = self.factory.return_app(message)
        if app is not None:
            await app.run()

    async def on_scheduled_event_create(self, event):
        # Refresh config
        self.config.read("config.ini")
        guild_id = str(event.guild.id)
        defense_channel = self.config[guild_id]["defense_channel"]
        game_server = self.config[guild_id]["game_server"]

        x, y = event.name.replace("/", "|").split("|")

        create_cfd(
            f"databases/{guild_id}.db",
            event.creator.id,
            event.id,
            event.creator.display_name,
            event.start_time,
            x,
            y,
            event.description,
        )
        embed = discord.Embed(color=Colors.SUCCESS)
        map_link = f"[{x}|{y}]({game_server}/position_details.php?x={x}&y={y})"
        message = f"""
        Submitted by: {event.creator.display_name}
        Coordinates: {map_link}
        Land Time: {str(event.start_time)}
        Defense Required: {event.description}
            """
        embed.add_field(name="New CFD", value=message)

        channel = get_channel_from_id(event.guild, defense_channel)
        await channel.send(embed=embed)

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


client = Core(intents=intents)
client.run(client.token)
