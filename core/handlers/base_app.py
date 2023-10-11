import configparser
from typing import List
import discord


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