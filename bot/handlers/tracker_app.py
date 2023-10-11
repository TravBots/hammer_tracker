from .base_app import BaseApp

from utils.errors import *
from utils.validators import *
from utils.decorators import *
from utils.printers import *
from funcs import *


class TrackerApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)
        print(f"Tracker params: {self.params}")

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
                print(
                    f"{self.keyword} is not a valid command for {self.__class__.__name__}"
                )
                await self.help()
        except PermissionError as e:
            response = incorrect_roles_error([str(e)])
            await self.message.channel.send(embed=response)

    @is_dev_or_admin_privs
    async def add(self, params):
        validated = validate_add_input(params)
        if validated:
            guild_id = str(self.message.guild.id)

            try:
                self.DB = self.config[guild_id]["database"]
            except KeyError:
                response = no_db_error()
            print(f"Params: {params}")
            coordinates = params.pop()
            coordinates = coordinates.replace("/", "|")
            print(f"Coordinates: {coordinates}")

            print(f"Params: {params}")
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
        DB = self.config[self.guild_id]["database"]
        game_server = self.config[self.guild_id]["game_server"]

        try:
            if isinstance(int(params[-1]), int):
                # This means it was `!tracker get ign 5`
                response = get_reports(
                    DB, " ".join(params[:-1]), game_server, params[-1]
                )
        except ValueError:
            print(params)
            response = get_one_report(DB, " ".join(params), game_server)
        except KeyError:
            response = no_db_error()
        await self.message.channel.send(embed=response)

    @is_dev_or_admin_privs
    async def delete(self, params, message):
        guild_id = str(message.guild.id)
        print(f"Params: {params}")
        ign = params[0]
        id = params[1]
        DB = self.config[guild_id]["database"]
        response = delete_report(DB, ign, id)

        await message.channel.send(embed=response)

    @is_dev_or_user_or_admin_privs
    async def list(self, message):
        guild_id = str(message.guild.id)
        self.DB = self.config[guild_id]["database"]

        response = list_all_names(self.DB)

        await message.channel.send(embed=response)

    async def help(self):
        response = give_help()

        await self.message.channel.send(embed=response)
