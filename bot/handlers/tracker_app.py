from .base_app import BaseApp

from utils.errors import *
from utils.validators import *
from utils.decorators import *
from utils.printers import *
from utils.logger import logger
from funcs import *
from utils.constants import ConfigKeys


class TrackerApp(BaseApp):
    def __init__(self, message, params):
        super().__init__(message, params)
        logger.info(f"Tracker params: {self.params}")

    async def run(self):
        try:
            if self.keyword == "add":
                await self.add(self.params)
            elif self.keyword == "get":
                await self.get(self.params)
            elif self.keyword == "delete":
                await self.delete(self.params, self.message)
            elif self.keyword == "list":
                await self.list(self.message)
            else:
                logger.error(
                    f"{self.keyword} is not a valid command for {self.__class__.__name__}"
                )
                await self.help()
        except Exception as e:
            logger.error(f"Error in TrackerApp: {e}")
            response = incorrect_roles_error([str(e)])
            await self.message.channel.send(embed=response)

    @is_dev_or_user_or_admin_privs
    async def add(self, params):
        logger.info(f"Params: {params}")

        self.DB = read_config_str(self.guild_id, "database", "")
        description = []
        url = None
        coords = None
        notes = []

        # Iterate through params
        for i, param in enumerate(params):
            # If we haven't found the URL yet
            if not url:
                if url_is_valid(param):
                    url = param
                    # If there's a next parameter, it's coords
                    if i + 1 < len(params):
                        coords = params[i + 1]
                        # Collect remaining params as notes
                        notes = " ".join(params[i + 2 :])
                    break
                else:
                    description.append(param)

        # Join collected description strings
        description = " ".join(description)
        logger.debug(
            f"IGN: {description}, URL: {url}, COORDS: {coords}, NOTES: {notes}"
        )

        if not coordinates_are_valid(coords):
            response = discord.Embed(color=Colors.ERROR)
            response.add_field(
                name="Error",
                value="Invalid coordinates, please use the format x|y",
            )
            await self.message.channel.send(embed=response)
            return

        if validate_unique_url(self.DB, url, description):
            # Build query and data tuple based on whether notes are provided
            base_query = "INSERT INTO HAMMERS (IGN, LINK, TIMESTAMP, COORDINATES{}) VALUES (?, ?, CURRENT_TIMESTAMP, ?{});"
            notes_part = ", NOTES" if notes else ""
            notes_placeholder = ", ?" if notes else ""
            query = base_query.format(notes_part, notes_placeholder)
            data = (
                (description, url, coords, notes)
                if notes
                else (description, url, coords)
            )
            logger.info(f"Query: {query}, Data: {data}")

            # Execute database operation
            with sqlite3.connect(self.DB) as conn:
                conn.execute(query, data)
                conn.commit()

            # Create response embed
            response = discord.Embed(color=Colors.SUCCESS)
            response.add_field(
                name="Success",
                value=f"Report for player {description} added to database",
            )
        else:
            logger.info(f"URL: {url} is not unique")
            response = discord.Embed(color=Colors.ERROR)
            response.add_field(
                name="Error",
                value="URL is not unique, please use a different URL",
            )

        await self.message.channel.send(embed=response)

    @is_dev_or_user_or_admin_privs
    async def get(self, params):
        self.DB = read_config_str(self.guild_id, ConfigKeys.DATABASE, "")
        game_server = read_config_str(self.guild_id, ConfigKeys.GAME_SERVER, "")

        try:
            if isinstance(int(params[-1]), int):
                # This means it was `!tracker get ign 5`
                response = get_reports(
                    self.DB, " ".join(params[:-1]), game_server, params[-1]
                )
        except ValueError:
            response = get_one_report(self.DB, " ".join(params), game_server)
        except KeyError:
            response = no_db_error()

        await self.message.channel.send(embed=response)

    @is_dev_or_admin_privs
    async def delete(self, params, message):
        logger.info(f"Params: {params}")
        ign = params[0]
        id = params[1]
        DB = read_config_str(self.guild_id, ConfigKeys.DATABASE, "")
        response = delete_report(DB, ign, id)

        await message.channel.send(embed=response)

    @is_dev_or_user_or_admin_privs
    async def list(self, message):
        self.DB = read_config_str(self.guild_id, ConfigKeys.DATABASE, "")
        response = list_all_names(self.DB)

        await message.channel.send(embed=response)

    async def help(self):
        response = give_help()

        await self.message.channel.send(embed=response)
