import discord
import re
import sqlite3

from typing import List

from utils.constants import dev_ids, pytest_id, MAP_MAX, MAP_MIN, FORWARDING_MAP
from utils.logger import logger


def coordinates_are_valid(coordinates: str, ignore_24_7: bool = False) -> bool:
    slash = "/" in coordinates
    pipe = "|" in coordinates

    if slash:
        xy = coordinates.split("/")
    elif pipe:
        xy = coordinates.split("|")
    else:
        return False

    if len(xy) != 2:
        return False

    try:
        x = int(xy[0])
        y = int(xy[1])
        if x > MAP_MAX or y > MAP_MAX or x < MAP_MIN or y < MAP_MIN:
            return False
        if ignore_24_7 and x == 24 and y == 7:
            return False
        return True
    except ValueError:
        return False


def url_is_valid(url: str):
    pattern = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    url_is_valid = bool(re.search(pattern, url))

    return url_is_valid


def validate_unique_url(db_name, url, ign) -> bool:
    try:
        with sqlite3.connect(db_name) as conn:
            query = "SELECT LINK FROM HAMMERS WHERE IGN = ?;"
            urls = [row[0] for row in conn.execute(query, (ign,))]
            logger.info(f"Found URLs for {ign}: {urls}")
            return url not in urls
    except sqlite3.Error as e:
        logger.error(f"Database error while validating URL: {e}")
        return False


def validate_role_exists(guild: discord.Guild, role):
    logger.info(f"Validating {role}")
    try:
        return role.lower() in [role.name.lower() for role in guild.roles]
    except AttributeError:
        return False


def user_is_guild_admin(message: discord.Message) -> bool:
    try:
        return message.author.guild_permissions.administrator
    except AttributeError:
        return False


def user_has_role(role, message) -> bool:
    """
    message: A discord.Message object, used to determine the user who sent the message
    role: The role to check against the roles of the user who sent the message

    return: boolean
    """
    try:
        return role.lower() in [a.name.lower() for a in message.author.roles]
    except AttributeError:
        return False


def is_dev(message) -> bool:
    return message.author.id in dev_ids or message.author.id == pytest_id


def should_forward(message: discord.Message):
    key = f"{message.guild.id}#{message.channel.id}"
    if key in FORWARDING_MAP:
        return FORWARDING_MAP[key]
    return None
