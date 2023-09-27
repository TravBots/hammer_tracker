from datetime import datetime
from typing import List

from utils.errors import *
from utils.validators import *
from utils.decorators import *
from funcs import *


class BaseApp:
    def __init__(
        self,
        message: discord.Message,
        params: List[str],
        config: configparser.ConfigParser,
    ):
        self.message = message
        self.guild_id = str(self.message.guild.id)
        self.db_path = f"databases/{self.guild_id}.db"
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
        try:
            if self.keyword == "init":
                await self._init()
            elif self.keyword == "info":
                await self._info()
            elif self.keyword == "set":
                await self._set_config_value(self.params)
            elif self.keyword == "link":
                await self.link(self.params)
            else:
                print(
                    f"{self.keyword} is not a valid command for {self.__class__.__name__}"
                )
        except PermissionError as e:
            response = incorrect_roles_error([str(e)])
            await self.message.channel.send(embed=response)

    @is_dev_or_guild_admin
    async def _init(self):
        print("Initializing database...")

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

    async def link(self, params):
        x, y = params[0].split("/")
        game_server = self.config[self.guild_id]["game_server"]
        embed = discord.Embed(color=Colors.SUCCESS)
        embed.add_field(
            name="",
            value=f"{game_server}/position_details.php?x={x}&y={y}",
        )
        await self.message.channel.send(embed=embed)


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


class DefApp(BaseApp):
    def __init__(self, message, params, config):
        super().__init__(message, params, config)

    async def run(self):
        try:
            if self.keyword == "list":
                await self.list(self.message)
            elif self.keyword == "send":
                await self.send(self.message, self.params)
            elif self.keyword == "leaderboard":
                await self.leaderboard(self.message)
            elif self.keyword == "log":
                await self.log(self.message)
            else:
                print(
                    f"{self.keyword} is not a valid command for {self.__class__.__name__}"
                )
        except PermissionError as e:
            response = incorrect_roles_error([str(e)])
            await self.message.channel.send(embed=response)

    @is_dev_or_anvil_or_admin_privs
    async def list(self, message):
        guild_id = str(message.guild.id)
        self.DB = self.config[guild_id]["database"]

        game_server = self.config[self.guild_id]["game_server"]
        response = list_open_cfds(self.DB, game_server)

        await message.channel.send(embed=response)

    @is_dev_or_anvil_or_admin_privs
    async def send(self, message: discord.Message, params):
        if isinstance(message.channel, discord.Thread):
            print("Message is in a thread")
            cfd_id = self._get_cfd_id_from_thread_id(message.channel.id)
        else:
            cfd_id = params[0]
        print(f"Params: {params}")
        amount_sent = int(params[-1].replace(",", ""))

        response = send_defense(self.db_path, cfd_id, amount_sent, message)

        await message.channel.send(embed=response)

    @is_dev_or_anvil_or_admin_privs
    async def leaderboard(self, message):
        guild_id = str(message.guild.id)
        self.DB = self.config[guild_id]["database"]

        response = get_leaderboard(self.db_path)

        await message.channel.send(embed=response)

    @is_dev_or_anvil_or_admin_privs
    async def log(self, message: discord.Message):
        if isinstance(message.channel, discord.Thread):
            cfd_id = self._get_cfd_id_from_thread_id(message.channel.id)
            query = "select submitted_by_id, amount_submitted, datetime(submitted_at, 'localtime') from submitted_defense where defense_call_id = ?"
            conn = sqlite3.connect(self.db_path)
            data = (cfd_id,)
            rows = conn.execute(query, data)

            result = ""

            for index, row in enumerate(rows):
                print(row)
                result += f"{index}. <@{row[0]}> ({row[1]:,} @ {row[2]})\n"
            conn.close()

            embed = discord.Embed(color=Colors.SUCCESS)
            embed.add_field(
                name="Defense submitted to this CFD",
                value=result,
            )

            await message.channel.send(embed=embed)

    def _get_cfd_id_from_thread_id(self, thread_id: int):
        query = "select defense_call_id from defense_threads where id = ?"
        conn = sqlite3.connect(self.db_path)
        data = (thread_id,)
        result = conn.execute(query, data)
        cfd_id = result.fetchone()[0]
        conn.close()
        return cfd_id


class Applications:
    PREFIX = "!"
    APPLICATIONS = {"boink": BoinkApp, "tracker": TrackerApp, "def": DefApp}
