import configparser
from typing import List
import discord

from utils.logger import logger
from utils.constants import BOT_SERVERS_DB_PATH


class BaseApp:
    def __init__(
        self,
        message: discord.Message,
        params: List[str],
        config: configparser.ConfigParser,
    ):
        self.message = message
        self.guild_id = str(self.message.guild.id) if self.message is not None else None
        self.db_path = (
            f"{BOT_SERVERS_DB_PATH}{self.guild_id}.db"
            if self.message is not None
            else None
        )
        self.keyword = params[0] if params is not None else None
        self.params = params[1:] if params is not None else None
        self.config = config
        self.config.read("config.ini")

        try:
            self.admin_role = self.config[self.guild_id]["admin_role"]
            self.user_role = self.config[self.guild_id]["user_role"]
            self.anvil_role = self.config[self.guild_id]["anvil_role"]
        except KeyError:
            logger.warn("Required role not set")

    async def run(self):
        raise NotImplementedError
