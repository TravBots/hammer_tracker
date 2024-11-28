import discord

from utils.logger import logger
from handlers.boink_app import BoinkApp
from handlers.def_app import DefApp
from handlers.tracker_app import TrackerApp
from handlers.base_app import BaseApp

"""
For each message posted in the server:
    * Validate that it is sent by a user, not a bot
    * Validate that it is a command meant for the bot
    * Separate the application (e.g. "tracker") from params (e.g. "get praxis")
    * Return an instance of a class representing the correct subsystem based on the provided application
"""

PREFIX = "!"
APPLICATIONS = ["boink", "def", "tracker"]


def _is_command(message: discord.Message) -> bool:
    applications = [f"{PREFIX}{application}" for application in APPLICATIONS]
    return message.content.startswith(tuple(applications))


def _is_bot_message(message: discord.Message) -> bool:
    return message.author.bot is True


def get_app(message) -> BaseApp:
    if _is_bot_message(message):
        return None

    if _is_command(message):
        app = message.content.split()[0].strip(PREFIX)
        params = message.content.split()[1:]
        logger.info(f"App: {app}, Params: {params}")

        if app == "boink":
            return BoinkApp(message, params)
        elif app == "def":
            return DefApp(message, params)
        elif app == "tracker":
            return TrackerApp(message, params)
        else:
            raise ValueError(f"Invalid application : {app}")
    else:
        return None
