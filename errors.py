import discord

from constants import Colors


def no_db_error():
    embed = discord.Embed(color=Colors.ERROR)
    embed.add_field(
        name="Error", value="Database not initialized. Try `!tracker init` first"
    )

    return embed


def no_link_error():
    embed = discord.Embed(color=Colors.ERROR)
    embed.add_field(
        name="Error", value="No link provided. See `!tracker help` for syntax help"
    )

    return embed


def incorrect_roles_error(required_roles: list):
    roles = "\n* ".join(required_roles)
    embed = discord.Embed(color=Colors.ERROR)
    embed.add_field(
        name="Error",
        value=f"One of the following roles are required for this command:\n* {roles}",
    )

    return embed


def invalid_input_error():
    embed = discord.Embed(color=Colors.ERROR)
    embed.add_field(
        name="Error",
        value="Invalid input provided. See `!tracker help` for syntax help",
    )

    return embed


def not_unique_error():
    embed = discord.Embed(color=Colors.ERROR)
    embed.add_field(name="Error", value="This report has already been recorded")

    return embed
