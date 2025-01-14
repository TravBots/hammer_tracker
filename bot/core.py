import datetime
import sqlite3
from typing import Any

import discord
from discord import app_commands
from discord.ext import tasks
from utils.factory import PREFIX, get_app
from funcs import (
    cancel_cfd,
    create_cfd,
    get_channel_from_id,
    insert_defense_thread,
)
from services.analytics_service import AnalyticsService
from utils.constants import ALLOW_FORWARDING, BOT_SERVERS_DB_PATH, Colors, ConfigKeys
from utils.logger import logger, periodic_log_check
from utils.validators import (
    coordinates_are_valid,
    should_forward,
    preprocess_coordinates,
)
from zoneinfo import ZoneInfo
from services.config_service import read_config_str, read_config_bool, read_config_int
from commands import COMMAND_LIST
from services.notification_service import NotificationService

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
        self.token = read_config_str(ConfigKeys.DEFAULT, ConfigKeys.TOKEN, "")
        self.analytics = AnalyticsService()
        self.notifications = NotificationService()

    async def setup_hook(self):
        # Add the commands directly
        for command in COMMAND_LIST:
            self.tree.add_command(command)

        # Start tasks
        self.close_threads.start()
        self.run_server_database_alerts.start()

        # Sync commands with Discord
        await self.tree.sync()

    async def on_message(self, message: discord.Message):
        if ALLOW_FORWARDING:
            result = should_forward(message)
            if result:
                guild_id, channel_id = result.split("#")
                guild = self.get_guild(int(guild_id))
                channel = guild.get_channel(int(channel_id))
                if message.content:
                    await channel.send(message.content)
                else:
                    await channel.send(embeds=message.embeds)

        app = get_app(message)
        logger.debug(f"App: {app}")
        if app is not None:
            self.analytics.record_command(
                app=message.content.split()[0].strip(PREFIX),
                full_command=message.content,
                discord_user_id=message.author.id,
                discord_user_name=message.author.display_name,
                discord_server_id=message.guild.id,
                discord_server_name=message.guild.name,
                travian_server_code=read_config_str(
                    message.guild.id, ConfigKeys.GAME_SERVER, ""
                ),
            )
            await app.run()
            return

        last_item = message.content.split(" ")[-1].replace("?", "")
        last_item = preprocess_coordinates(last_item)
        ignore_24_7 = read_config_bool(message.guild.id, "ignore_24_7", False)

        if coordinates_are_valid(last_item, ignore_24_7):
            slash = "/" in last_item
            pipe = "|" in last_item

            if slash:
                xy = last_item.split("/")
            elif pipe:
                xy = last_item.split("|")
            x = xy[0].strip()
            y = xy[1].strip()
            game_server = read_config_str(message.guild.id, ConfigKeys.GAME_SERVER, "")
            embed = discord.Embed(color=Colors.SUCCESS)
            embed.add_field(
                name="",
                value=f"{game_server}/position_details.php?x={x}&y={y}",
            )
            await message.channel.send(embed=embed)

    async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
        guild_id = str(event.guild.id)
        defense_channel = read_config_str(guild_id, ConfigKeys.DEFENSE_CHANNEL, "")
        game_server = read_config_str(guild_id, ConfigKeys.GAME_SERVER, "")

        x, y = event.location.replace("/", "|").split("|")

        cfd_id = create_cfd(
            db_name=f"{BOT_SERVERS_DB_PATH}{guild_id}.db",
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
            db_name=f"{BOT_SERVERS_DB_PATH}{guild_id}.db",
            defense_thread_id=thread.id,
            cfd_id=cfd_id,
            name=thread.name,
            jump_url=thread.jump_url,
        )

        await thread.send(
            content="Respond to this CFD in the thread below :point_down:"
        )

    async def on_scheduled_event_delete(self, event):
        guild_id = str(event.guild.id)
        cancel_cfd(f"{BOT_SERVERS_DB_PATH}{guild_id}.db", event.id)

    async def on_scheduled_event_update(self, before, after):
        """
        End events after they start
        """
        logger.info(before.status)
        logger.info(after.status)
        if after.status == discord.EventStatus.active:
            await after.end()

    @tasks.loop(minutes=10.0)
    async def close_threads(self):
        # Get defense discord.Channel from config channel
        # Get threads in Channel
        # For each thread, get associated cfd
        # If cfd land_time is in the past, archive the thread
        for guild in self.guilds:
            try:
                clean_up_threads = read_config_bool(
                    guild.id, ConfigKeys.CLEAN_UP_THREADS, False
                )
                if clean_up_threads:
                    defense_channel = read_config_str(
                        guild.id, ConfigKeys.DEFENSE_CHANNEL, ""
                    )
                    channel = get_channel_from_id(guild, defense_channel)

                    if len(channel.threads) == 0:
                        continue

                    logger.info(f"Cleaning up threads for {guild}")
                    conn = sqlite3.connect(f"{BOT_SERVERS_DB_PATH}{guild.id}.db")
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

                        land_time = datetime.datetime.strptime(
                            cfd_thread[0].replace("+", ".").split(".")[0],
                            "%Y-%m-%d %H:%M:%S",
                        )

                        if land_time < datetime.datetime.utcnow():
                            logger.info(f"Archiving thread {thread.name}")
                            await thread.edit(archived=True)
            except KeyError as e:
                logger.error(f"Failed to clean up threads for {guild}")
                logger.error(e)

    @tasks.loop(hours=24)
    async def run_server_database_alerts(self):
        await self.wait_until_ready()
        logger.info("Running server database alerts")

        for guild in self.guilds:
            try:
                await self.notifications.work(
                    guild, read_config_int(guild.id, ConfigKeys.ALERTS, 0)
                )
            except KeyError as e:
                logger.error(f"Failed to check alerts for {guild}")
                logger.error(e)


if __name__ == "__main__":
    # Init logging first
    periodic_log_check()

    client = Core(intents=intents)
    client.run(client.token)
