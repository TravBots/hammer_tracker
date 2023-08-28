import discord
import configparser
from typing import Any

from errors import *
from funcs import *
from hero import *
from validators import *

intents = discord.Intents.all()
intents.message_content = True


class Tracker(discord.Client):
    def __init__(
        self,
        *,
        intents: discord.Intents,
        **options: Any,
    ) -> None:
        super().__init__(intents=intents, **options)

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.TOKEN = self.config["default"]["token"]

    async def on_message(self, message):
        if message.author == client.user:
            return

        # Refresh config
        self.config.read("config.ini")

        try:
            # Get guild_id and DB
            guild_id = str(message.guild.id)
            DB = self.config[guild_id]["database"]

            # Get admin_role and user_role
            admin_role = self.config[guild_id]["admin_role"]
            user_role = self.config[guild_id]["user_role"]
        except KeyError:
            pass

        if message.content.startswith("!tracker init"):
            if user_is_guild_admin(message):
                response = init(message)
                self.config.read("config.ini")
                DB = self.config[guild_id]["database"]
                create_hammers = get_sql_by_path("sql/create_table_hammers.sql")
                create_defense_calls = get_sql_by_path(
                    "sql/create_table_defense_calls.sql"
                )
                create_submitted_defense = get_sql_by_path(
                    "sql/create_table_submitted_defense.sql"
                )
                execute_sql(DB, create_hammers)
                execute_sql(DB, create_defense_calls)
                execute_sql(DB, create_submitted_defense)

                await message.channel.send(embed=response)

        elif message.content.startswith("!tracker set admin "):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                server_role = " ".join(post[3:])

                if validate_role_exists(message.guild, server_role) is False:
                    response = invalid_role_error(server_role)
                    await message.channel.send(embed=response)
                    return

                try:
                    response = set_admin(str(message.guild.id), server_role)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([admin_role])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker set user "):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                server_role = " ".join(post[3:])

                if validate_role_exists(message.guild, server_role) is False:
                    response = invalid_role_error(server_role)
                    await message.channel.send(embed=response)
                    return

                try:
                    response = set_user(str(message.guild.id), server_role)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([admin_role])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker set server "):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                game_server = post[3]

                try:
                    response = set_game_server(str(message.guild.id), game_server)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([admin_role])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker set defense channel "):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                channel_id = post[4]

                try:
                    response = set_defense_channel(str(message.guild.id), channel_id)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([admin_role])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker info"):
            if user_has_role(admin_role, message):
                try:
                    guild_id = str(message.guild.id)
                    self.DB = self.config[guild_id]["database"]
                    response = give_info(self.DB, guild_id)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([admin_role])
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker add "):
            if user_has_role(admin_role, message):
                try:
                    post = message.content.split(" ")
                    validated = validate_add_input(post)
                    if validated:
                        guild_id = str(message.guild.id)
                        self.DB = self.config[guild_id]["database"]
                        coordinates = post.pop()
                        coordinates = coordinates.replace("/", "|")
                        link = post.pop()
                        ign = post[2:]
                        if len(ign) > 1:
                            ign = " ".join(ign).lower()
                        else:
                            ign = ign[0].lower()
                        unique = validate_unique_url(self.DB, link, ign)
                        if unique:
                            response = add_report(self.DB, ign, link, coordinates)
                        else:
                            response = not_unique_error()
                    else:
                        response = invalid_input_error()
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([admin_role])
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker get "):
            if user_has_role(admin_role, message) or user_has_role(user_role, message):
                post = message.content.split(" ")
                DB = self.config[guild_id]["database"]
                game_server = config[guild_id]["game_server"]

                try:
                    if isinstance(int(post[-1]), int):
                        response = get_reports(
                            DB, " ".join(post[2:-1]), game_server, post[-1]
                        )
                except ValueError:
                    response = get_one_report(DB, " ".join(post[2:]), game_server)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([user_role, admin_role])
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker delete"):
            if user_has_role(admin_role, message):
                guild_id = str(message.guild.id)
                post = message.content.split(" ")
                ign = post[2]
                id = post[3]
                DB = self.config[guild_id]["database"]
                response = delete_report(DB, ign, id)
            else:
                response = incorrect_roles_error([admin_role])
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker list all"):
            if user_has_role(admin_role, message) or user_has_role(user_role, message):
                guild_id = str(message.guild.id)
                self.DB = self.config[guild_id]["database"]

                response = list_all_names(self.DB)
            else:
                response = incorrect_roles_error([user_role, admin_role])
            await message.channel.send(embed=response)

        elif message.content.startswith("!tracker"):
            response = give_help()

            await message.channel.send(embed=response)

        elif message.content.startswith("!dev info"):
            print(message)
            print(message.guild.owner)

            await message.delete()

        elif message.content.startswith("!gear "):
            url = message.content.split(" ")[1]
            response = get_hero_items(url)

            await message.channel.send(embed=response)

        else:
            return

    async def on_scheduled_event_create(self, event):
        # Refresh config
        self.config.read("config.ini")
        guild_id = str(event.guild.id)
        defense_channel = self.config[guild_id]["defense_channel"]
        game_server = self.config[guild_id]["game_server"]

        embed = discord.Embed(color=Colors.SUCCESS)
        x, y = event.name.replace("/", "|").split("|")
        map_link = f"[{x}|{y}]({game_server}/position_details.php?x={x}&y={y})"
        message = f"""
        Submitted by: {event.creator.display_name}
        Coordinates: {map_link}
        Land Time: {str(event.start_time)}
        Defense Required: {event.description}
            """
        embed.add_field(name="New CFD", value=message)

        channel = get_channel_from_id(event.guild, defense_channel)
        await channel.send(embed=embed)


client = Tracker(intents=intents)
client.run(client.TOKEN)
