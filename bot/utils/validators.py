import discord
import re
import sqlite3

from typing import List

from utils.constants import dev_ids, pytest_id, MAP_MAX, MAP_MIN
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
    conn = sqlite3.connect(db_name)

    query = "SELECT LINK FROM HAMMERS WHERE IGN = ?;"
    data = (ign,)

    data = conn.execute(query, data)

    urls = []

    for row in data:
        urls.append(row[0])

    conn.close()

    if url in urls:
        unique = False
    else:
        unique = True

    return unique


def validate_add_input(params: List[str]) -> bool:
    """
    Add input is very specific. It should be a list of string values, defined as:
    [
        ign_part_1: str,
        ign_part_2: str,
        url: str,
        coordinates: str
    ]
    where `coordinates` are a string such as `1|2` or `1/2`. Note that an IGN
    can have multiple parts. This is the result of a multi-word IGN, such as
    `Here We Go Again`
    We'll use multiple individual validators bundled into this one convenience method
    """
    logger.info(f"Validating {params}")

    coordinates = params[-1]
    url = params[-2]

    if not coordinates_are_valid(coordinates):
        return False

    if not url_is_valid(url):
        return False

    return True


def validate_role_exists(guild: discord.Guild, role):
    logger.info(f"Validating {role}")
    return role.lower() in [role.name.lower() for role in guild.roles]


def user_is_guild_admin(message: discord.Message) -> bool:
    return message.author.guild_permissions.administrator


def user_has_role(role, message) -> bool:
    """
    message: A discord.Message object, used to determine the user who sent the message
    role: The role to check against the roles of the user who sent the message

    return: boolean
    """
    return role.lower() in [a.name.lower() for a in message.author.roles]


def is_dev(message) -> bool:
    return message.author.id in dev_ids or message.author.id == pytest_id
