import discord

from utils.logger import logger
from handlers.boink_app import BoinkApp
from handlers.def_app import DefApp
from handlers.tracker_app import TrackerApp
from handlers.base_app import BaseApp
from utils.constants import APPLICATIONS, Apps


PREFIX = "!"


def _is_command(message: discord.Message) -> bool:
    applications = [f"{PREFIX}{application}" for application in APPLICATIONS]
    return message.content.startswith(tuple(applications))


def _is_bot_message(message: discord.Message) -> bool:
    return message.author.bot is True


def get_app(message) -> BaseApp:
    logger.debug(
        f"Message received: {message.content}; author isBot?: {message.author.bot}; webhook_id: {message.webhook_id}; author id: {message.author.id}"
    )
    # Ignore messages sent by bots; let webhooks pass through for ci/cd
    if _is_bot_message(message):
        if message.webhook_id is None:
            return None

    # Validate that the message starts with a bot command
    if _is_command(message):
        app = message.content.split()[0].strip(PREFIX)
        params = message.content.split()[1:]
        logger.info(f"App: {app}, Params: {params}")

        # Return an instance of the correct application class
        if app == Apps.BOINK:
            return BoinkApp(message, params)
        elif app == Apps.DEF:
            return DefApp(message, params)
        elif app == Apps.TRACKER:
            return TrackerApp(message, params)
        else:
            raise ValueError(f"Invalid application : {app}")
    else:
        return None
