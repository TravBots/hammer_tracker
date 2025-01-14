import datetime
import sqlite3
import string
import discord
from utils.constants import ConfigKeys, NotificationFlags, Colors
from utils.logger import logger
from services.config_service import read_config_str
from funcs import get_alliance_tag_from_id, get_connection_path


class NotificationService:
    """Service to manage notifications and alerts across Discord servers"""

    def __init__(self):
        logger.info("Notification Service initialized")

    ######### UTIL FUNCTIONS #########

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

    async def _message_exists(
        self, channel: discord.TextChannel, message_content: str
    ) -> bool:
        """Check if message already exists in recent channel history"""
        messages = [msg async for msg in channel.history(limit=5)]
        return any(message.content == message_content for message in messages)

    ######### ALERT FUNCTIONS #########

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
            current_alliance = get_alliance_tag_from_id(conn, player_data[2])
            old_alliance = get_alliance_tag_from_id(conn, player_data[3])

            if current_alliance is None or current_alliance == "":
                alert_message = f"Player {player_data[1]} left alliance {old_alliance}."
            elif old_alliance is None or old_alliance == "":
                alert_message = (
                    f"Player {player_data[1]} joined alliance {current_alliance}."
                )
            else:
                alert_message = (
                    f"Player {player_data[1]} has changed alliances from "
                    f"**{old_alliance}** to **{current_alliance}**"
                )

            # Check recent message history
            if await self._message_exists(channel, alert_message):
                logger.info(
                    f"Skipping alliance change alert for {player_data[1]} because it was already sent."
                )
                return

            await channel.send(alert_message)
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
                    alert_message = f"Player {row[1]} has deleted their account."
                    if await self._message_exists(channel, alert_message):
                        logger.info(
                            f"Skipping alert for {row[1]} because it was already sent."
                        )
                        return
                    await channel.send(alert_message)

        except Exception as e:
            logger.error(f"Error sending alerts for guild {guild.id}: {e}")

    async def _send_new_village_alert(
        self, conn: sqlite3.Connection, guild: discord.Guild
    ) -> None:
        """Send an alert about new villages to the specified channel"""
        enemy_aliances = read_config_str(guild.id, ConfigKeys.ENEMY_ALLIANCES, "")
        if enemy_aliances == "":
            logger.info(f"No enemy alliances found for guild {guild.id}")
            return

        home_quad = read_config_str(guild.id, ConfigKeys.HOME_QUAD, "")
        if home_quad == "":
            logger.info(f"No home quad found for guild {guild.id}")
            return

        notif_channel = read_config_str(guild.id, ConfigKeys.NOTIF_CHANNEL, "")
        if notif_channel == "":
            logger.info(f"No notification channel found for guild {guild.id}")
            return

        # Define coordinate conditions based on quadrant
        coord_conditions = {
            "NW": "x_coordinate < 0 AND y_coordinate > 0",
            "NE": "x_coordinate > 0 AND y_coordinate > 0",
            "SW": "x_coordinate < 0 AND y_coordinate < 0",
            "SE": "x_coordinate > 0 AND y_coordinate < 0",
        }

        quad_condition = coord_conditions.get(home_quad.upper())
        if not quad_condition:
            logger.error(f"Invalid home quadrant specified: {home_quad}")
            return

        for alliance in enemy_aliances.split(","):
            logger.info(f"Checking for new villages from alliance {alliance}")

            query = f"""
            SELECT 
                player_name,
                x_coordinate,
                y_coordinate,
                population,
                alliance_tag
            FROM v_new_villages 
            WHERE alliance_tag = ? 
            AND {quad_condition}
            """

            # Convert cursor to list to get count
            rows = list(conn.execute(query, (alliance.strip(),)))

            channel = discord.utils.get(guild.text_channels, name=notif_channel)
            if channel is None:
                logger.error(f"Could not find notification channel {notif_channel}")
                return

            for row in rows:
                logger.info(f"Sending new village alert for {row[0]}")

                embed = discord.Embed(color=Colors.WARNING)
                embed.add_field(
                    name="New Village Detected!",
                    value=(
                        f"**Player:** {row[0]}\n"
                        f"**Alliance:** {row[4]}\n"
                        f"**Population:** {row[3]}\n"
                        f"**Location:** [{row[1]}|{row[2]}]"
                    ),
                )

                # Convert the embed to a string representation for comparison
                embed_dict = embed.to_dict()
                embed_str = str(embed_dict)

                if await self._message_exists(channel, embed_str):
                    logger.info(
                        f"Skipping new village alert for {row[0]} because it was already sent."
                    )
                    continue

                await channel.send(embed=embed)

            logger.info(f"Sent {len(rows)} new village alerts for alliance {alliance}")

    ######### WORK FUNCTION #########

    async def work(self, guild: discord.Guild, alert_code: int) -> None:
        """Main work function for the notification service"""
        logger.info(
            f"Processing alerts for guild {guild.id} with alert code {alert_code}"
        )
        if alert_code == 0:
            logger.info(f"No alerts to process for guild {guild.id}")
            return

        # Get game server config and connect to DB
        game_server = read_config_str(guild.id, ConfigKeys.GAME_SERVER, "")

        with sqlite3.connect(get_connection_path(game_server)) as conn:
            # Check each flag and process corresponding alerts
            if alert_code & NotificationFlags.PLAYER_DELETED:
                logger.info("Sending player deleted alerts")
                await self._send_player_deleted_alert(conn, guild)

            if alert_code & NotificationFlags.ALLIANCE_CHANGE:
                logger.info("Sending alliance change alerts")
                await self._send_alliance_change_alert(conn, guild)

            if alert_code & NotificationFlags.NEW_VILLAGE:
                logger.info("Sending new village alerts")
                await self._send_new_village_alert(conn, guild)

        logger.info(f"Processed alerts for guild {guild.id}")
