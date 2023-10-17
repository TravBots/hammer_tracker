from .base_app import BaseApp
import discord

import sqlite3
import pandas as pd

from utils.constants import BOT_SERVERS_DB_PATH, GAME_SERVERS_DB_PATH
from utils.errors import *
from utils.validators import *
from utils.decorators import *
from utils.printers import *
from utils.logger import logger
from funcs import *


class BoinkApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)

    async def run(self):
        try:
            if self.keyword == "init":
                await self._init()
            elif self.keyword == "info":
                await self._info()
            elif self.keyword == "set":
                await self._set_config_value(self.params)
            elif self.keyword == "search":
                await self.search(self.params, self.message)
            else:
                logger.error(
                    f"{self.keyword} is not a valid command for {self.__class__.__name__}"
                )
        except PermissionError as e:
            response = incorrect_roles_error([str(e)])
            await self.message.channel.send(embed=response)

    @is_dev_or_guild_admin
    async def _init(self):
        logger.info("Initializing database...")

        response = init(self.config, self.message)
        self.config.read("config.ini")
        DB = self.config[self.guild_id]["database"]

        create_hammers = get_sql_by_path("sql/create_table_hammers.sql")
        create_defense_calls = get_sql_by_path("sql/create_table_defense_calls.sql")
        create_submitted_defense = get_sql_by_path(
            "sql/create_table_submitted_defense.sql"
        )
        create_defense_threads = get_sql_by_path("sql/create_table_defense_threads.sql")

        for query in [
            create_hammers,
            create_defense_calls,
            create_submitted_defense,
            create_defense_threads,
        ]:
            execute_sql(DB, query)

        await self.message.channel.send(embed=response)

    @is_dev_or_admin_privs
    async def _info(self):
        # TODO: Handle getting/setting admin and user roles
        # Maybe offload it to the util function to get.
        # Change to user_is_app_admin and user_is_app_user?
        try:
            response = give_info(self.config, self.guild_id)
        except KeyError:
            response = no_db_error()

        await self.message.channel.send(embed=response)

    @is_dev_or_guild_admin
    async def _set_config_value(self, params):
        # Params might be: admin bot user
        # and we want `admin` as the setting_name
        # and `bot user` as the setting value
        # NOTE: This does limit setting_name to one word

        setting_name = params[0]
        logger.info(f"setting_name: {setting_name}")
        setting_value = " ".join(params[1:])
        try:
            with open("config.ini", "w") as conf:
                self.config[self.guild_id][setting_name] = setting_value
                self.config.write(conf)
            embed = discord.Embed(color=Colors.SUCCESS)
            embed.add_field(
                name="Success", value=f"Set {setting_name} as {setting_value}"
            )
        except Exception as e:
            logger.error(e)
            embed = discord.Embed(color=Colors.ERROR)
            embed.add_field(
                name="Error",
                value=f"Failed to set {setting_name} as {setting_value}",
            )

        await self.message.channel.send(embed=embed)

    @is_dev_or_user_or_admin_privs
    async def search(self, params, message):
        guild_id = str(message.guild.id)
        self.DB = self.config[guild_id]["database"]

        ign = " ".join(params).lower()
        # TODO: Don't hardocde am3.db. Dynamically get db nick.
        cnx = sqlite3.connect(f"{GAME_SERVERS_DB_PATH}am3.db")
        query = f"select * from map_history where lower(player_name) like '{ign}%'"
        df = pd.read_sql_query(query, cnx)

        # Get largest timestamp from the df['timestamp'] column
        timestamp = df["inserted_at"].max()
        player = df["player_name"][0]
        player_id = df["player_id"][0]
        df = df[df["inserted_at"] == timestamp]
        df = df[df["player_name"] == player]
        df = df.sort_values(by=["population"], ascending=False)
        if not df.empty:
            link = f"[View on Travstat](https://www.travstat.com/players/{player_id})"
            embed = discord.Embed(title=player, color=Colors.SUCCESS)
            embed.description = link
            embed.add_field(
                name="Village Name | X | Y | Population",
                value=rows_to_piped_strings(
                    df,
                    ["village_name", "x_coordinate", "y_coordinate", "population"],
                ),
                inline=False,
            )
        else:
            embed = discord.Embed(color=Colors.ERROR)
            embed.add_field(
                name="Error", value="No results found for " + ign + " in the map"
            )

        await message.channel.send(embed=embed)
