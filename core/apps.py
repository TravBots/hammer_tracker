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
        self.guild_id = str(self.message.guild.id)
        self.keyword = params[0]
        self.params = params[1:]
        self.config = config
        self.config.read("config.ini")

        try:
            self.admin_role = self.config[self.guild_id]["admin_role"]
            self.user_role = self.config[self.guild_id]["user_role"]
            self.anvil_role = self.config[self.guild_id]["anvil_role"]
        except KeyError:
            print("Required role not set")

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
            await self._set_config_value(self.params)

    async def _init(self):
        print("Initializing database...")
        if is_dev(self.message) or user_is_guild_admin(self.message):
            response = init(self.config, self.message)
            self.config.read("config.ini")
            DB = self.config[self.guild_id]["database"]

            create_hammers = get_sql_by_path("sql/create_table_hammers.sql")
            create_defense_calls = get_sql_by_path("sql/create_table_defense_calls.sql")
            create_submitted_defense = get_sql_by_path(
                "sql/create_table_submitted_defense.sql"
            )

            for query in [
                create_hammers,
                create_defense_calls,
                create_submitted_defense,
            ]:
                execute_sql(DB, query)

            await self.message.channel.send(embed=response)

    async def _info(self):
        # TODO: Handle getting/setting admin and user roles
        # Maybe offload it to the util function to get.
        # Change to user_is_app_admin and user_is_app_user?
        if is_dev(self.message) or user_has_role(self.admin_role, self.message):
            try:
                response = give_info(self.config, self.guild_id)
            except KeyError:
                response = no_db_error()
        else:
            response = incorrect_roles_error([self.admin_role])
        await self.message.channel.send(embed=response)

    async def _set_config_value(self, params):
        # Params might be: admin bot user
        # and we want `admin` as the setting_name
        # and `bot user` as the setting value
        # NOTE: This does limit setting_name to one word
        if is_dev(self.message) or user_is_guild_admin(self.message):
            setting_name = params[0]
            print(f"setting_name: {setting_name}")
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
                print(e)
                embed = discord.Embed(color=Colors.ERROR)
                embed.add_field(
                    name="Error",
                    value=f"Failed to set {setting_name} as {setting_value}",
                )

            await self.message.channel.send(embed=embed)


class TrackerApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)
        print(f"Tracker params: {self.params}")

    async def run(self):
        if self.keyword == "add":
            await self.add(self.params)
        elif self.keyword == "get":
            await self.get(self.params)
        elif self.keyword == "delete":
            await self.delete(self.params, self.message)
        elif self.keyword == "list":
            await self.list(self.message)
        else:
            await self.help()

    async def add(self, params):
        if is_dev(self.message) or user_has_role(self.admin_role, self.message):
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
        else:
            response = incorrect_roles_error([self.admin_role])
        await self.message.channel.send(embed=response)

    async def get(self, params):
        if (
            is_dev(self.message)
            or user_has_role(self.admin_role, self.message)
            or user_has_role(self.user_role, self.message)
        ):
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
        else:
            response = incorrect_roles_error([self.user_role, self.admin_role])
        await self.message.channel.send(embed=response)

    async def delete(self, params, message):
        if is_dev(message) or user_has_role(self.admin_role, message):
            guild_id = str(message.guild.id)
            print(f"Params: {params}")
            ign = params[0]
            id = params[1]
            DB = self.config[guild_id]["database"]
            response = delete_report(DB, ign, id)
        else:
            response = incorrect_roles_error([self.admin_role])
        await message.channel.send(embed=response)

    async def list(self, message):
        if (
            is_dev(message)
            or user_has_role(self.admin_role, message)
            or user_has_role(self.user_role, message)
        ):
            guild_id = str(message.guild.id)
            self.DB = self.config[guild_id]["database"]

            response = list_all_names(self.DB)
        else:
            response = incorrect_roles_error([self.user_role, self.admin_role])
        await message.channel.send(embed=response)

    async def help(self):
        response = give_help()

        await self.message.channel.send(embed=response)


class DefApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)

    async def run(self):
        if self.keyword == "list":
            await self.list(self.message)
        elif self.keyword == "send":
            await self.send(self.message, self.params)
        elif self.keyword == "leaderboard":
            await self.leaderboard(self.message)

    async def list(self, message):
        if (
            is_dev(message)
            or user_has_role(self.anvil_role, message)
            or user_is_guild_admin(message)
        ):
            guild_id = str(message.guild.id)
            self.DB = self.config[guild_id]["database"]

            response = list_open_cfds(self.DB)
        else:
            response = incorrect_roles_error([self.user_role, self.admin_role])
        await message.channel.send(embed=response)

    async def send(self, message, params):
        if (
            is_dev(message)
            or user_has_role(self.anvil_role, message)
            or user_is_guild_admin(message)
        ):
            guild_id = str(message.guild.id)
            self.DB = self.config[guild_id]["database"]
            print(f"Params: {params}")
            cfd_id = params[0]
            amount_sent = int(params[1].replace(",", ""))

            response = send_defense(
                f"databases/{guild_id}.db", cfd_id, amount_sent, message
            )
        else:
            response = incorrect_roles_error([self.anvil_role])
        await message.channel.send(embed=response)

    async def leaderboard(self, message):
        if (
            is_dev(message)
            or user_has_role(self.anvil_role, message)
            or user_is_guild_admin(message)
        ):
            guild_id = str(message.guild.id)
            self.DB = self.config[guild_id]["database"]

            response = get_leaderboard(f"databases/{guild_id}.db")
        else:
            response = incorrect_roles_error([self.user_role, self.admin_role])

        await message.channel.send(embed=response)


class Applications:
    PREFIX = "!"
    APPLICATIONS = {"boink": BoinkApp, "tracker": TrackerApp, "def": DefApp}
