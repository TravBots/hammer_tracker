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

    async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
        # Refresh config
        self.config.read("config.ini")
        guild_id = str(event.guild.id)
        defense_channel = self.config[guild_id]["defense_channel"]
        game_server = self.config[guild_id]["game_server"]

        x, y = event.location.replace("/", "|").split("|")

        create_cfd(
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
        message = f"""
        Submitted by: {event.creator.display_name}
        Coordinates: {map_link}
        Land Time: {str(event.start_time)}
        Defense Required: {event.description}
            """
        embed.add_field(name="New CFD", value=message)

        channel = get_channel_from_id(event.guild, defense_channel)
        cfd_message = await channel.send(embed=embed)
        thread = await channel.create_thread(name=event.name, message=cfd_message)
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


client = Core(intents=intents)
client.run(client.token)
