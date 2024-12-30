import datetime
import sqlite3
import string
import discord
from utils.constants import ConfigKeys
from utils.logger import logger
from services.config_service import read_config_str
from funcs import get_alliance_tag_from_id, get_connection_path


class NotificationService:
    """Service to manage notifications and alerts across Discord servers"""

    def __init__(self):
        logger.info("Notification Service initialized")

    def _is_data_too_old(self, timestamp_str: str) -> bool:
        """Check if the data timestamp is more than 1 day old"""
        timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d")
        return timestamp < datetime.datetime.utcnow() - datetime.timedelta(days=1)

    def _format_channel_name(self, player_name: str) -> str:
        """Format player name into valid Discord channel name"""
        channel_name = player_name.replace(" ", "-").lower()
        return channel_name.translate(str.maketrans("", "", string.punctuation))

    def _find_player_channel(
        self, guild: discord.Guild, player_name: str
    ) -> discord.TextChannel:
        """Find Discord channel matching player name"""
        channel_name = self._format_channel_name(player_name)
        logger.info(f"Checking for channel {channel_name}")

        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel is not None:
            logger.info(f"Found channel {channel}")
        return channel

    async def send_alerts_for_guild(self, guild: discord.Guild) -> None:
        """Send alliance change alerts for a specific guild"""
        logger.info(f"Sending alerts for {str(guild.id)}")

        # Get game server config and connect to DB
        game_server = read_config_str(guild.id, ConfigKeys.GAME_SERVER, "")

        with sqlite3.connect(get_connection_path(game_server)) as conn:
            await self._send_player_deleted_alert(conn, guild)
            await self._send_alliance_change_alert(conn, guild)

    async def _send_alliance_change_alert(
        self, conn: sqlite3.Connection, guild: discord.Guild
    ) -> None:
        """Send an alert about player changes to the specified channel"""
        try:
            # Get all players that changed alliances
            query = "select * from v_player_change where alliance_changed=1 and current_population>0"
            rows = conn.execute(query)

            for row in rows:
                if self._is_data_too_old(row[11]):
                    logger.info("Skipping all alerts because the data is too old.")
                    return

                channel = self._find_player_channel(guild, row[1])
                if channel is not None:
                    await self._send_player_alert(conn, channel, row)

        except Exception as e:
            logger.error(f"Error sending alerts for guild {guild.id}: {e}")

    async def _send_player_alert(
        self, conn: sqlite3.Connection, channel: discord.TextChannel, player_data: tuple
    ) -> None:
        """Send an alert about player changes to the specified channel"""
        try:
            # Player changed alliances
            old_alliance = get_alliance_tag_from_id(conn, player_data[3])
            new_alliance = get_alliance_tag_from_id(conn, player_data[2])

            await channel.send(
                f"Player {player_data[1]} has changed alliances from "
                f"**{old_alliance}** to **{new_alliance}**"
            )
        except Exception as e:
            logger.error(f"Error sending player alert: {e}")

    async def _send_player_deleted_alert(
        self, conn: sqlite3.Connection, guild: discord.Guild
    ) -> None:
        """Send an alert about player deletion to the specified channel"""
        try:
            # Get all players that changed alliances
            query = "select * from v_player_change where current_population=0"
            rows = conn.execute(query)

            for row in rows:
                if self._is_data_too_old(row[11]):
                    logger.info("Skipping all alerts because the data is too old.")
                    return

                channel = self._find_player_channel(guild, row[1])
                if channel is not None:
                    await channel.send(f"Player {row[1]} has deleted their account.")

        except Exception as e:
            logger.error(f"Error sending alerts for guild {guild.id}: {e}")
