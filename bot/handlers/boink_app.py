import sqlite3

import discord
import pandas as pd
from funcs import execute_sql, get_sql_by_path, give_info, init, process_name
from utils.constants import GAME_SERVERS_DB_PATH, Colors

# from utils.validators import *
from utils.decorators import (
    is_dev_or_admin_privs,
    is_dev_or_guild_admin,
    is_dev_or_user_or_admin_privs,
)
from utils.errors import incorrect_roles_error, invalid_input_error, no_db_error
from utils.logger import logger
from utils.printers import rows_to_piped_strings

from .base_app import BaseApp


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
                response = invalid_input_error()
                await self.message.channel.send(embed=response)
        except Exception as e:
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

    def _get_connection_path(self, message) -> str:
        path = f"{GAME_SERVERS_DB_PATH}"

        game_server = self.config[str(message.guild.id)]["game_server"]

        server_number, speed, domain = game_server.split(".")[0:3]
        server_number = server_number.split("ts")[1]

        domains = {
            "america": "am",
            "europe": "eu",
            "arabics": "arab"
        }
        # if game_server == "https://ts3.x1.america.travian.com":
        #     path += "am3.db"
        # elif game_server == "https://ts2.x1.america.travian.com":
        #     path += "am2.db"

        database_name = f"{domains[domain]}{server_number}.db"
        logger.debug(f"database_name: {database_name}")
        return path+database_name

    @is_dev_or_user_or_admin_privs
    async def search(self, params, message):
        guild_id = str(message.guild.id)
        self.DB = self.config[guild_id]["database"]
        ign = " ".join(params).lower()

        try:
            cnx = sqlite3.connect(self._get_connection_path(message))

            # First attempt an exact match
            query = f"select * from x_world where lower(player_name) = '{ign}'"
            df = pd.read_sql_query(query, cnx)

            if df.empty:
                # If no exact match, try a partial match
                logger.info(f"No exact match found for {ign}. Trying partial match")
                query = f"select * from x_world where lower(player_name) like '{ign}%'"
                df = pd.read_sql_query(query, cnx)

            # Get largest timestamp from the df['timestamp'] column
            # timestamp = df["inserted_at"].max()
            player = df["player_name"][0]
            player_id = df["player_id"][0]
            # df = df[df["inserted_at"] == timestamp]
            df = df[df["player_name"] == player]
            df = df.sort_values(by=["population"], ascending=False)

            df["village_name"] = df["village_name"].apply(process_name)

            # TODO: Don't hardcode am3 link. Dynamically get server link.
            df["village_markdown"] = (
                "["
                + df["village_name"]
                + "](https://ts2.x1.america.travian.com/position_details.php?x="
                + df["x_coordinate"].astype(str)
                + "&y="
                + df["y_coordinate"].astype(str)
                + ")"
            )
            df.loc[df["capital"] == 1, "village_markdown"] = (
                df["village_markdown"] + "*"
            )
            df["coords"] = (
                df["x_coordinate"].astype(str) + "|" + df["y_coordinate"].astype(str)
            )

            if not df.empty:
                link = (
                    f"[View on Travstat](https://www.travstat.com/players/{player_id}) | "
                    f"[View in-game](https://ts2.x1.america.travian.com/profile/{player_id})"
                )
                embed = discord.Embed(title=player, color=Colors.SUCCESS)
                embed.description = (
                    link + "\n\n" + "**Village Name | X|Y | Population**\n"
                )
                embed.description += rows_to_piped_strings(
                    pd.DataFrame(df),
                    ["village_markdown", "coords", "population"],
                )

                await message.channel.send(embed=embed)
            else:
                raise Exception("No results found")
        except Exception as e:
            logger.warn(f"Sending failure message due to exception {e}")
            embed = discord.Embed(color=Colors.ERROR)
            embed.add_field(
                name="Error", value="No results found for " + ign + " in the map"
            )
            await message.channel.send(embed=embed)
