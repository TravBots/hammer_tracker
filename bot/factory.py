import configparser
from typing import Any, List, Union

import discord
from apps import Applications
from utils.logger import logger


class AppFactory:
    """
    For each message posted in the server:
        * Validate that it is sent by a user, not a bot
        * Validate that it is a command meant for the bot
        * Separate the application (e.g. "tracker") from params (e.g. "get praxis")
        * Return an instance of a class representing the correct subsystem based on the provided application
    """

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

    def _is_command(self, message: discord.Message) -> bool:
        applications = [
            f"{Applications.PREFIX}{application}"
            for application in Applications.APPLICATIONS
        ]
        return message.content.startswith(tuple(applications))

    def _is_bot_message(self, message: discord.Message) -> bool:
        return message.author.bot is True

    def _get_application(self, message: discord.Message) -> Union[str, Any]:
        logger.info(message.content.split()[0].strip(Applications.PREFIX))
        return Applications.APPLICATIONS.get(
            message.content.split()[0].strip(Applications.PREFIX)
        )

    def _get_params(self, message: discord.Message) -> Union[List[str], Any]:
        return message.content.split()[1:]

    def return_app(self, message: discord.Message) -> Any:
        if self._is_bot_message(message):
            return None

        if self._is_command(message):
            app = self._get_application(message)
            params = self._get_params(message)
            logger.info(f"Initial params: {params}")
            application = app(message, params, self.config)

            return application
        else:
            return None
