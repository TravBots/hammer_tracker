from .base_app import BaseApp

from utils.errors import *
from utils.validators import *
from utils.decorators import *
from utils.printers import *
from funcs import *


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
