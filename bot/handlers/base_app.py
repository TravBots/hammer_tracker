import configparser
from typing import List
import discord

from utils.logger import logger
from utils.constants import BOT_SERVERS_DB_PATH
from utils.config_manager import read_config_str


class BaseApp:
    def __init__(
        self,
        message: discord.Message,
        params: List[str],
    ):
        self.message = message
        self.guild_id = str(self.message.guild.id)
        self.db_path = f"{BOT_SERVERS_DB_PATH}{self.guild_id}.db"
        self.keyword = params[0]
        self.params = params[1:]

        self.admin_role = read_config_str(self.guild_id, "admin_role", "")
        self.user_role = read_config_str(self.guild_id, "user_role", "")
        self.anvil_role = read_config_str(self.guild_id, "anvil_role", "")

    async def run(self):
        raise NotImplementedError
