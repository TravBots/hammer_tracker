from typing import List

from errors import *
from funcs import *
from validators import *


class BaseApp:
    def __init__(
        self,
        message: discord.Message,
        params: List[str],
        config: configparser.ConfigParser,
    ):
        self.message = message
        self.keyword = params[0]
        self.params = params[1:]
        self.config = config

    async def run(self):
        raise NotImplementedError


class BoinkApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)

    async def run(self):
        if self.keyword == "init":
            await self._init()
        elif self.keyword == "info":
            await self._info()
        elif self.keyword == "set":
            # Handle "set admin", "set user", and "set server"
            # Write to config
            pass

    async def _init(self):
        print("Initializing database...")
        if user_is_guild_admin(self.message):
            response = init(self.config, self.message)
            self.config.read("config.ini")
            DB = self.config[self.message.guild_id]["database"]
            create_hammers = get_sql_by_path("sql/create_table_hammers.sql")
            create_defense_calls = get_sql_by_path("sql/create_table_defense_calls.sql")
            create_submitted_defense = get_sql_by_path(
                "sql/create_table_submitted_defense.sql"
            )
            execute_sql(DB, create_hammers)
            execute_sql(DB, create_defense_calls)
            execute_sql(DB, create_submitted_defense)

            await self.message.channel.send(embed=response)

    async def _info(self):
        # TODO: Handle getting/setting admin and user roles
        # Maybe offload it to the util function to get.
        # Change to user_is_app_admin and user_is_app_user?
        if user_has_role(self.admin_role, self.message):
            try:
                guild_id = self.message.guild.id
                response = give_info(self.config, guild_id)
            except KeyError:
                response = no_db_error()
        else:
            response = incorrect_roles_error([self.admin_role])
        await self.message.channel.send(embed=response)

    #     elif message.content.startswith("!tracker set admin "):
    #         if user_is_guild_admin(message):
    #             post = message.content.split(" ")
    #             server_role = " ".join(post[3:])

    #             if validate_role_exists(message.guild, server_role) is False:
    #                 response = invalid_role_error(server_role)
    #                 await message.channel.send(embed=response)
    #                 return

    #             try:
    #                 response = set_admin(
    #                     self.config, str(message.guild.id), server_role
    #                 )
    #             except KeyError:
    #                 response = no_db_error()
    #         else:
    #             response = incorrect_roles_error([admin_role])
    #         self.config.read("config.ini")
    #         await message.channel.send(embed=response)

    #     elif message.content.startswith("!tracker set user "):
    #         if user_is_guild_admin(message):
    #             post = message.content.split(" ")
    #             server_role = " ".join(post[3:])

    #             if validate_role_exists(message.guild, server_role) is False:
    #                 response = invalid_role_error(server_role)
    #                 await message.channel.send(embed=response)
    #                 return

    #             try:
    #                 response = set_user(self.config, str(message.guild.id), server_role)
    #             except KeyError:
    #                 response = no_db_error()
    #         else:
    #             response = incorrect_roles_error([admin_role])
    #         self.config.read("config.ini")
    #         await message.channel.send(embed=response)

    #     elif message.content.startswith("!tracker set server "):
    #         if user_is_guild_admin(message):
    #             post = message.content.split(" ")
    #             game_server = post[3]

    #             try:
    #                 response = set_game_server(
    #                     self.config, str(message.guild.id), game_server
    #                 )
    #             except KeyError:
    #                 response = no_db_error()
    #         else:
    #             response = incorrect_roles_error([admin_role])
    #         self.config.read("config.ini")
    #         await message.channel.send(embed=response)


class TrackerApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)

    async def run(self):
        if self.keyword == "add":
            pass

    async def add(self, params):
        if user_has_role(self.admin_role, self.message):
            validated = validate_add_input(params)
            if validated:
                guild_id = str(self.message.guild.id)

                try:
                    self.DB = self.config[guild_id]["database"]
                except KeyError:
                    response = no_db_error()

                coordinates = params.pop()
                coordinates = coordinates.replace("/", "|")

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
        else:
            response = incorrect_roles_error([admin_role])
        await self.message.channel.send(embed=response)

    async def get(self, params):
        if user_has_role(admin_role, self.message) or user_has_role(
            user_role, self.message
        ):
            DB = self.config[guild_id]["database"]
            game_server = self.config[guild_id]["game_server"]

            try:
                if isinstance(int(params[-1]), int):
                    # This means it was `!tracker get ign 5`
                    response = get_reports(
                        DB, " ".join(params[2:-1]), game_server, params[-1]
                    )
            except ValueError:
                response = get_one_report(DB, " ".join(params[2:]), game_server)
            except KeyError:
                response = no_db_error()
        else:
            response = incorrect_roles_error([user_role, admin_role])
        await self.message.channel.send(embed=response)

    #     elif message.content.startswith("!tracker delete"):
    #         if user_has_role(admin_role, message):
    #             guild_id = str(message.guild.id)
    #             post = message.content.split(" ")
    #             ign = post[2]
    #             id = post[3]
    #             DB = self.config[guild_id]["database"]
    #             response = delete_report(DB, ign, id)
    #         else:
    #             response = incorrect_roles_error([admin_role])
    #         await message.channel.send(embed=response)

    #     elif message.content.startswith("!tracker list all"):
    #         if user_has_role(admin_role, message) or user_has_role(user_role, message):
    #             guild_id = str(message.guild.id)
    #             self.DB = self.config[guild_id]["database"]

    #             response = list_all_names(self.DB)
    #         else:
    #             response = incorrect_roles_error([user_role, admin_role])
    #         await message.channel.send(embed=response)

    #     elif message.content.startswith("!tracker"):
    #         response = give_help()

    #         await message.channel.send(embed=response)


class DefApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)

    #     elif message.content.startswith("!def set anvil role "):
    #         if user_is_guild_admin(message):
    #             post = message.content.split(" ")
    #             server_role = " ".join(post[4:])

    #             if validate_role_exists(message.guild, server_role) is False:
    #                 response = invalid_role_error(server_role)
    #                 await message.channel.send(embed=response)
    #                 return

    #             try:
    #                 response = set_anvil(
    #                     self.config, str(message.guild.id), server_role
    #                 )
    #             except KeyError:
    #                 response = no_db_error()
    #         else:
    #             response = incorrect_roles_error([admin_role])
    #         self.config.read("config.ini")
    #         await message.channel.send(embed=response)

    #     elif message.content.startswith("!def set channel "):
    #         if user_is_guild_admin(message):
    #             post = message.content.split(" ")
    #             channel_id = post[3]

    #             try:
    #                 response = set_defense_channel(
    #                     self.config, str(message.guild.id), channel_id
    #                 )
    #             except KeyError:
    #                 response = no_db_error()
    #         else:
    #             response = incorrect_roles_error([admin_role])
    #         self.config.read("config.ini")
    #         await message.channel.send(embed=response)

    #     elif message.content.startswith("!def list open"):
    #         if user_has_role(anvil_role, message) or user_is_guild_admin(message):
    #             guild_id = str(message.guild.id)
    #             self.DB = self.config[guild_id]["database"]

    #             response = list_open_cfds(self.DB)
    #         else:
    #             response = incorrect_roles_error([user_role, admin_role])
    #         await message.channel.send(embed=response)

    #     elif message.content.startswith("!def send"):
    #         if user_has_role(anvil_role, message) or user_is_guild_admin(message):
    #             guild_id = str(message.guild.id)
    #             self.DB = self.config[guild_id]["database"]
    #             post = message.content.split(" ")
    #             cfd_id = post[2]
    #             amount_sent = int(post[3].replace(",", ""))

    #             response = send_defense(
    #                 f"databases/{guild_id}.db", cfd_id, amount_sent, message
    #             )
    #         else:
    #             response = incorrect_roles_error([anvil_role])
    #         await message.channel.send(embed=response)

    #     elif message.content.startswith("!def leaderboard"):
    #         if user_has_role(anvil_role, message) or user_is_guild_admin(message):
    #             guild_id = str(message.guild.id)
    #             self.DB = self.config[guild_id]["database"]

    #             response = get_leaderboard(f"databases/{guild_id}.db")
    #         else:
    #             response = incorrect_roles_error([user_role, admin_role])
    #         await message.channel.send(embed=response)
    #     else:
    #         return


class Applications:
    PREFIX = "!"
    APPLICATIONS = {"boink": BoinkApp, "tracker": TrackerApp, "def": DefApp}
