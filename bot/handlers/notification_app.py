from .base_app import BaseApp

import sqlite3

from utils.decorators import *
from utils.constants import *
from utils.logger import logger
from utils.errors import *
from funcs import *


class NotificationApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)

    async def run(self):
        try:
            if self.keyword == "force_run":
                await self.force_run()
            elif self.keyword == "subscribe":
                await self.subscribe()
            elif self.keyword == "list":
                await self.list()
            elif self.keyword == "unsubscribe":
                await self.unsubscribe()
            else:
                logger.error(
                    f"{self.keyword} is not a valid command for {self.__class__.__name__}"
                )
                response = invalid_input_error()
                await self.message.channel.send(embed=response)
        except Exception as e:
            response = incorrect_roles_error([str(e)])
            await self.message.channel.send(embed=response)

    @is_dev
    async def force_run(self):
        passed = False
        try:
            await self.run_notification_task()
            passed = True
        except Exception as e:
            logger.error(f"Failed to run for error: {e}")

        if passed:
            embed = discord.Embed(
                title="Force Run Notification Task Completed",
                color=Colors.SUCCESS,
            )
        else:
            embed = discord.Embed(
                title="Force Run Notification Task Failed",
                color=Colors.ERROR,
            )

        await self.message.channel.send(embed=embed)

    @is_dev_or_user_or_admin_privs
    async def subscribe(self):
        notif_code = self.params[0]
        player_name = self.params[1]

        # TODO: Insert validation around notification codes

        player_id = get_player_id_for_player(player_name)
        if player_id is None:
            embed = discord.Embed(
                title="Subscribe Failed",
                description=f"Player `{player_name}` not found",
                color=Colors.ERROR,
            )
            await self.message.channel.send(embed=embed)
            return

        channel_id = self.message.channel.mention
        discord_id = self.message.author.mention

        DB = self.config[self.guild_id]["database"]
        query = """
            INSERT INTO notification_subscriptions (CHANNEL_ID, NOTIFICATION_CODE, TARGET_ID, DISCORD_ID)
            VALUES (?, ?, ?, ?)
        """
        values = (channel_id, notif_code, player_id, discord_id)
        execute_sql_with_values(DB, query, values)

        embed = discord.Embed(
            title="Subscribe Success",
            description=f"{discord_id} on {channel_id} subscribed to notification: `{notif_code}`, for player `{player_name}`",
            color=Colors.SUCCESS,
        )
        await self.message.channel.send(embed=embed)

    @is_dev_or_user_or_admin_privs
    async def list(self):
        DB = self.config[self.guild_id]["database"]
        query = "SELECT * FROM notification_subscriptions;"

        results = query_sql(DB, query)

        logger.info(f"Results: {results}")

        embed = discord.Embed(
            title="Notification Subscriptions",
            color=Colors.SUCCESS,
        )

        for result in results:
            logger.info(f"Result: {result}")
            embed.add_field(
                name=f"{result['NOTIFICATION_CODE']} - {result['TARGET_ID']}",
                value=f"Channel: {result['CHANNEL_ID']}\nDiscord: {result['DISCORD_ID']}",
                inline=False,
            )

        await self.message.channel.send(embed=embed)

    @is_dev_or_user_or_admin_privs
    async def unsubscribe(self):
        notif_code = self.params[0]
        player_name = self.params[1]

        # TODO: Insert validation around notification codes

        player_id = get_player_id_for_player(player_name)
        if player_id is None:
            embed = discord.Embed(
                title="Subscribe Failed",
                description=f"Player `{player_name}` not found",
                color=Colors.ERROR,
            )
            await self.message.channel.send(embed=embed)
            return

        channel_id = self.message.channel.mention
        discord_id = self.message.author.mention

        DB = self.config[self.guild_id]["database"]
        query = """
            DELETE FROM notification_subscriptions
            WHERE CHANNEL_ID = ?
            AND NOTIFICATION_CODE = ?
            AND TARGET_ID = ?
            AND DISCORD_ID = ?
        """
        values = (channel_id, notif_code, player_id, discord_id)
        execute_sql_with_values(DB, query, values)

        embed = discord.Embed(
            title="Unsubscribe Success",
            description=f"{discord_id} on {channel_id} unsubscribed from notification: `{notif_code}`, for player `{player_name}`",
            color=Colors.SUCCESS,
        )
        await self.message.channel.send(embed=embed)

    async def run_notification_task(self):
        logger.info("Running notification task")
        DB = self.config[self.guild_id]["database"]

        # TODO: Don't hardocde am3.db. Dynamically get db nick.
        cnx = sqlite3.connect(f"{GAME_SERVERS_DB_PATH}am3.db")

        # Query to pull two most recent unique inserted_at dates from the map_history table
        query = """
            SELECT DISTINCT inserted_at
            FROM map_history
            ORDER BY inserted_at DESC
            LIMIT 2
        """

        # Execute query and store results
        cursor = cnx.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        logger.info(f"Results: {results}")

        logger.info("Finished notification task")
