import discord
import re
import sqlite3


def roles_are_valid(message, guild_id, config) -> bool:
    admin_role = config[guild_id]["admin_role"].lower()
    user_role = config[guild_id]["user_role"].lower()
    author_roles = [a.name.lower() for a in message.author.roles]

    return admin_role in author_roles or user_role in author_roles


def coordinates_are_valid(coordinates) -> bool:
    if "/" not in coordinates and "|" not in coordinates:
        return False

    return True


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


def validate_add_input(post) -> bool:
    print(f"Validating {post}")

    # Coordinates should be last item included
    if not coordinates_are_valid(post[-1]):
        return False

    pattern = (
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )

    url = [bool(re.search(pattern, part)) for part in post[:-1]]

    if url[-1] is True:
        return True
    else:
        return False


def user_is_guild_admin(message: discord.Message) -> bool:
    return message.author.guild_permissions.administrator


def user_has_role(role, message) -> bool:
    """
    message: A discord.Message object, used to determine the user who sent the message
    role: The role to check against the roles of the user who sent the message

    return: boolean
    """
    return role.lower() in [a.name.lower() for a in message.author.roles]
