from .base_app import BaseApp

import json

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

        if notif_code not in Notifications.get_values():
            embed = discord.Embed(
                title="Subscribe Failed",
                description=f"Notification code `{notif_code}` not found",
                color=Colors.ERROR,
            )
            await self.message.channel.send(embed=embed)
            return

        if notif_code == Notifications.NEW_VILLAGE:
            await self.handle_new_village_subscription()
        elif notif_code == Notifications.ALLIANCE_QUAD_NEW_VILLAGE:
            await self.handle_alliance_quad_new_village_subscription()

    async def handle_alliance_quad_new_village_subscription(self):
        alliance_name = self.params[1]
        quad = self.params[2]

        if quad not in ["NW", "NE", "SW", "SE"]:
            embed = discord.Embed(
                title="Subscribe Failed",
                description=f"Quad `{quad}` not found",
                color=Colors.ERROR,
            )
            await self.message.channel.send(embed=embed)
            return

        alliance_id = get_alliance_id_for_alliance(alliance_name)
        guild_id = self.message.guild.id
        channel_id = self.message.channel.mention
        discord_id = self.message.author.mention
        extra_info = '{"quad": "' + quad + '"}'

        DB = self.config[self.guild_id]["database"]
        query = """
            INSERT INTO notification_subscriptions (GUILD_ID, CHANNEL_ID, NOTIFICATION_CODE, TARGET_ID, DISCORD_ID, EXTRA_INFO)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (
            guild_id,
            channel_id,
            Notifications.ALLIANCE_QUAD_NEW_VILLAGE,
            alliance_id,
            discord_id,
            extra_info,
        )
        execute_sql_with_values(DB, query, values)

        embed = discord.Embed(
            title="Subscribe Success",
            description=f"{discord_id} on {channel_id} subscribed to notification: `{Notifications.ALLIANCE_QUAD_NEW_VILLAGE}`, for alliance `{alliance_name}`, quad `{quad}`",
            color=Colors.SUCCESS,
        )
        await self.message.channel.send(embed=embed)

    async def handle_new_village_subscription(self):
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

        guild_id = self.message.guild.id
        channel_id = self.message.channel.mention
        discord_id = self.message.author.mention

        DB = self.config[self.guild_id]["database"]
        query = """
            INSERT INTO notification_subscriptions (GUILD_ID, CHANNEL_ID, NOTIFICATION_CODE, TARGET_ID, DISCORD_ID, EXTRA_INFO)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (
            guild_id,
            channel_id,
            Notifications.NEW_VILLAGE,
            player_id,
            discord_id,
            "",
        )
        execute_sql_with_values(DB, query, values)

        embed = discord.Embed(
            title="Subscribe Success",
            description=f"{discord_id} on {channel_id} subscribed to notification: `{Notifications.NEW_VILLAGE}`, for player `{player_name}`",
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
            embed.add_field(
                name=f"{result['NOTIFICATION_CODE']} - {result['TARGET_ID']}",
                value=f"Channel: {result['CHANNEL_ID']}\nDiscord: {result['DISCORD_ID']}",
                inline=False,
            )

        await self.message.channel.send(embed=embed)

    @is_dev_or_user_or_admin_privs
    async def unsubscribe(self):
        notif_code = self.params[0]

        if notif_code not in Notifications.get_values():
            embed = discord.Embed(
                title="Subscribe Failed",
                description=f"Notification code `{notif_code}` not found",
                color=Colors.ERROR,
            )
            await self.message.channel.send(embed=embed)
            return

        if notif_code == Notifications.NEW_VILLAGE:
            await self.handle_new_village_unsubscription()
        elif notif_code == Notifications.ALLIANCE_QUAD_NEW_VILLAGE:
            await self.handle_alliance_quad_new_village_unsubscription()

    async def handle_alliance_quad_new_village_unsubscription(self):
        alliance_name = self.params[1]
        alliance_id = get_alliance_id_for_alliance(alliance_name)
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
        values = (
            channel_id,
            Notifications.ALLIANCE_QUAD_NEW_VILLAGE,
            alliance_id,
            discord_id,
        )
        execute_sql_with_values(DB, query, values)

        embed = discord.Embed(
            title="Unsubscribe Success",
            description=f"{discord_id} on {channel_id} unsubscribed from notification: `{Notifications.ALLIANCE_QUAD_NEW_VILLAGE}`, for alliance `{alliance_name}`, quad `{quad}`",
            color=Colors.SUCCESS,
        )
        await self.message.channel.send(embed=embed)

    async def handle_new_village_unsubscription(self):
        player_name = self.params[1]

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
        values = (channel_id, Notifications.NEW_VILLAGE, player_id, discord_id)
        execute_sql_with_values(DB, query, values)

        embed = discord.Embed(
            title="Unsubscribe Success",
            description=f"{discord_id} on {channel_id} unsubscribed from notification: `{Notifications.NEW_VILLAGE}`, for player `{player_name}`",
            color=Colors.SUCCESS,
        )
        await self.message.channel.send(embed=embed)

    async def run_notification_task(self):
        logger.info("****** Running notification task ******")

        # TODO: Don't hardocde am3.db. Dynamically get db nick.
        game_DB = f"{GAME_SERVERS_DB_PATH}am3.db"
        discord_DB = f"{BOT_SERVERS_DB_PATH}{self.config['default']['guild_id']}.db"

        (new_date, old_date) = self.get_latest_two_dates(game_DB)
        logger.info(f"[NotifTask] Old date: {old_date}, New date: {new_date}")

        notif_embeds = []
        for notif in Notifications.get_values():
            # Skip the actual get_values call
            if notif == Notifications.get_values:
                continue
            logger.info(f"[NotifTask] Processing notification: {notif}")

            # Get subscriptions for the notification code
            subscriptions = self.get_subscriptions_for_notification_code(
                discord_DB, notif
            )

            for sub in subscriptions:
                logger.info(f"[NotifTask] Processing subscription: {sub}")
                notif = self.notif_action_handler(
                    notif, sub, old_date, new_date, game_DB
                )
                if notif is not None:
                    notif_embeds.append(notif)

        logger.info("****** Finished notification task ******")
        return notif_embeds

    def get_latest_two_dates(self, DB):
        # Query to pull two most recent unique inserted_at dates from the map_history table
        query = """
            SELECT DISTINCT inserted_at
            FROM map_history
            ORDER BY inserted_at DESC
            LIMIT 2
        """
        results = query_sql(DB, query)
        # logger.debug(f"Results: {results}")
        return (results[0]["inserted_at"], results[1]["inserted_at"])

    def get_subscriptions_for_notification_code(self, DB, notif_code):
        query = """
            SELECT *
            FROM notification_subscriptions
            WHERE NOTIFICATION_CODE = ?
        """

        results = query_sql_with_values(DB, query, (notif_code,))

        logger.debug(f"Results: {results}")
        return results

    def notif_action_handler(self, notif_code, subscription, old_date, new_date, DB):
        if notif_code == Notifications.NEW_VILLAGE:
            return self.new_village_handler(subscription, old_date, new_date, DB)
        elif notif_code == Notifications.ALLIANCE_QUAD_NEW_VILLAGE:
            return self.alliance_quad_new_village_handler(
                subscription, old_date, new_date, DB
            )
        else:
            logger.error(f"Unknown notification code: {notif_code}")
            raise Exception(f"Unknown notification code: {notif_code}")

    def alliance_quad_new_village_handler(self, subscription, old_date, new_date, DB):
        alliance_id = subscription["TARGET_ID"]
        discord_id = subscription["DISCORD_ID"]
        channel_id = subscription["CHANNEL_ID"]
        extra_info = subscription["EXTRA_INFO"]
        quad = json.loads(extra_info)["quad"]

        logger.info(
            f"[NotifTask] alliance_id: {alliance_id}, discord_id: {discord_id}, channel_id: {channel_id}, quad: {quad}"
        )

        # Get all village_ids that have 1 insert_count in v_village_ages
        query = """
            SELECT village_id, x_coordinate, y_coordinate
            FROM v_village_ages
            WHERE insert_count = 1
            AND alliance_id = ?
        """
        values = (alliance_id,)
        results = query_sql_with_values(DB, query, values)

        logger.info(f"[NotifTask] Results size: {results.__len__()}")
        logger.info(f"[NotifTask] Results: {results}")

        x0, x1, y0, y1 = get_quad_limits(quad)
        logger.info(f"[NotifTask] Quad limits: {x0}, {y0}, {x1}, {y1}")

        final_results = []
        for result in results:
            x = result["x_coordinate"]
            y = result["y_coordinate"]
            if x >= x0 and x <= x1 and y >= y0 and y <= y1:
                final_results.append(result)

        logger.info(f"[NotifTask] Final results size: {final_results.__len__()}")
        logger.info(f"[NotifTask] Final results: {final_results}")

        if final_results.__len__() > 0:
            logger.info(
                f"[NotifTask] Sending notification for alliance: {alliance_id}; discord: {discord_id}, channel: {channel_id}, quad: {quad}"
            )
            embed = discord.Embed(
                title="New Village Notification",
                description=f"Alliance `{alliance_id}` gained the following new villages in the `{quad}` quad",
                color=Colors.SUCCESS,
            )
            embed.add_field(
                name="Villages",
                value=final_results,
                inline=False,
            )
            return (embed, subscription)

    def new_village_handler(self, subscription, old_date, new_date, DB):
        target_id = subscription["TARGET_ID"]
        discord_id = subscription["DISCORD_ID"]
        channel_id = subscription["CHANNEL_ID"]

        # Get the number of villages the player has for both old and new date
        query = """
            SELECT COUNT(*)
            FROM map_history
            WHERE inserted_at = ?
            AND player_id = ?
        """
        old_count = query_sql_with_values(DB, query, (old_date, target_id))[0][
            "COUNT(*)"
        ]
        new_count = query_sql_with_values(DB, query, (new_date, target_id))[0][
            "COUNT(*)"
        ]
        logger.info(f"[NotifTask] Old count: {old_count}, New count: {new_count}")

        # If the player has more villages, send a notification
        if new_count > old_count:
            logger.info(
                f"[NotifTask] Sending notification for target: {target_id}; discord: {discord_id}, channel: {channel_id}"
            )
            embed = discord.Embed(
                title="New Village Notification",
                description=f"Player `{target_id}` has gained a new village",
                color=Colors.SUCCESS,
            )
            return (embed, subscription)
        else:
            logger.info(f"[NotifTask] No notification for sub: {subscription}")
            return None
