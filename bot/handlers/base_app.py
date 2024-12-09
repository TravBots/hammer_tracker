from typing import List
import discord

from utils.constants import BOT_SERVERS_DB_PATH, ConfigKeys
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

        self.admin_role = read_config_str(self.guild_id, ConfigKeys.ADMIN_ROLE, "")
        self.user_role = read_config_str(self.guild_id, ConfigKeys.USER_ROLE, "")
        self.anvil_role = read_config_str(self.guild_id, ConfigKeys.ANVIL_ROLE, "")

    async def run(self):
        raise NotImplementedError
