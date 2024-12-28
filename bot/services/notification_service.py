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

    async def send_alerts_for_guild(self, guild: discord.Guild) -> None:
        """Send alliance change alerts for a specific guild"""
        logger.info(f"Sending alerts for {str(guild.id)}")

        # Get game server config and connect to DB
        game_server = read_config_str(guild.id, ConfigKeys.GAME_SERVER, "")
        conn = sqlite3.connect(get_connection_path(game_server))

        await self._send_player_deleted_alert(conn, guild)

        try:
            # Get all players that changed alliances
            query = "select * from v_player_change where alliance_changed=1 and current_population>0"
            rows = conn.execute(query)

            for row in rows:
                # Check if data is too old
                timestamp = datetime.datetime.strptime(row[11], "%Y-%m-%d")
                if timestamp < datetime.datetime.utcnow() - datetime.timedelta(days=1):
                    logger.info("Skipping all alerts because the data is too old.")
                    return

                # Format channel name from player name
                channel_name = row[1].replace(" ", "-").lower()
                channel_name = channel_name.translate(
                    str.maketrans("", "", string.punctuation)
                )
                logger.info(f"Checking for channel {channel_name}")

                # Find matching channel
                channel = discord.utils.get(guild.text_channels, name=channel_name)
                if channel is not None:
                    logger.info(f"Found channel {channel}")
                    await self._send_player_alert(conn, channel, row)

        except Exception as e:
            logger.error(f"Error sending alerts for guild {guild.id}: {e}")
        finally:
            conn.close()

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
                # Check if data is too old
                timestamp = datetime.datetime.strptime(row[11], "%Y-%m-%d")
                if timestamp < datetime.datetime.now() - datetime.timedelta(days=1):
                    logger.info("Skipping all alerts because the data is too old.")
                    return

                # Format channel name from player name
                channel_name = row[1].replace(" ", "-").lower()
                channel_name = channel_name.translate(
                    str.maketrans("", "", string.punctuation)
                )
                logger.debug(f"Checking for channel {channel_name}")

                # Find matching channel
                channel = discord.utils.get(guild.text_channels, name=channel_name)
                if channel is not None:
                    logger.info(f"Found channel {channel}")
                    await channel.send(f"Player {row[1]} has deleted their account.")

        except Exception as e:
            logger.error(f"Error sending alerts for guild {guild.id}: {e}")
