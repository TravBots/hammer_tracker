from .base_app import BaseApp

from utils.errors import *
from utils.validators import *
from utils.decorators import *
from utils.printers import *
from utils.logger import logger
from funcs import *


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
            response = incorrect_roles_error([str(e)])
            await self.message.channel.send(embed=response)

    @is_dev_or_admin_privs
    async def add(self, params):
        validated = validate_add_input(params)
        if validated:
            try:
                self.DB = read_config_str(self.guild_id, "database", "")
            except KeyError:
                response = no_db_error()
                await self.message.channel.send(embed=response)
                return

            logger.info(f"Params: {params}")
            coordinates = params.pop()
            coordinates = coordinates.replace("/", "|")
            logger.info(f"Coordinates: {coordinates}")

            logger.info(f"Params: {params}")
            link = params.pop()

            ign = params
            ign = " ".join(ign).lower()

            unique = validate_unique_url(self.DB, link, ign)
            if unique:
                response = add_report(self.DB, ign, link, coordinates)
            else:
                response = not_unique_error()
        else:
            response = invalid_input_error()
        await self.message.channel.send(embed=response)

    @is_dev_or_user_or_admin_privs
    async def get(self, params):
        self.DB = read_config_str(self.guild_id, "database", "")
        game_server = read_config_str(self.guild_id, "game_server", "")

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
        DB = read_config_str(self.guild_id, "database", "")
        response = delete_report(DB, ign, id)

        await message.channel.send(embed=response)

    @is_dev_or_user_or_admin_privs
    async def list(self, message):
        self.DB = read_config_str(self.guild_id, "database", "")
        response = list_all_names(self.DB)

        await message.channel.send(embed=response)

    async def help(self):
        response = give_help()

        await self.message.channel.send(embed=response)
