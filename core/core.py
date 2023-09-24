import discord
from discord.ext import tasks
import configparser
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from utils.errors import *
from funcs import *
from utils.hero import *
from utils.validators import *

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
        self.config: configparser.ConfigParser = configparser.ConfigParser()
        self.config.read("config.ini")

        self.token = self.config["default"]["token"]

        self.factory = AppFactory()

    async def setup_hook(self):
        self.close_threads.start()

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

    @tasks.loop(seconds=10.0)
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
                        return

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


client = Core(intents=intents)
client.run(client.token)
