import discord
import configparser
from typing import Any

from errors import *
from funcs import *
from hero import *
from validators import *
from constants import *

intents = discord.Intents.all()
intents.message_content = True


class Tracker(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: Any,) -> None:
        super().__init__(intents=intents, **options)

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.TOKEN = self.config["default"]["token"]

        self.guild_cache = {}

    async def on_message(self, message):
        if message.author == client.user:
            return

        # Refresh config
        self.config.read("config.ini")

        # Get guild_id and DB
        guild_id = str(message.guild.id)
        record_exists = self.cache_guild_record(guild_id)
        if(not record_exists):
           pass

        self.handle_command(message.content, self.guild_cache[guild_id])
        
    # @TODO: Make this proper caching by checking if record already exists before creating
    def cache_guild_rcord(self, guild_id):
        try:
            guild_record = {}
            guild_record[Config.ID] = guild_id
            guild_record[Config.DATABASE] = self.config[self.guild_id][Config.DATABASE]

            # Get admin_role and user_role
            guild_record[Config.ADMIN_ROLE] = self.config[self.guild_id][Config.ADMIN_ROLE]
            guild_record[Config.USER_ROLE] = self.config[self.guild_id][Config.USER_ROLE]
            guild_record[Config.ANVIL_ROLE] = self.config[self.guild_id][Config.ANVIL_ROLE]

            self.guild_cache[guild_id] = guild_record
            return True
        except KeyError:
            return False

    async def handle_command(self, command: str, message, guild_record):
        if command.startswith(Commands.Tracker.INIT):
            print("Initializing database...")
            if user_is_guild_admin(message):
                response = init(self.config, message)
                self.config.read("config.ini")
                DB = guild_record[Config.DATABASE]
                
                create_hammers = get_sql_by_path("tracker/sql/create_table_hammers.sql")
                create_defense_calls = get_sql_by_path("tracker/sql/create_table_defense_calls.sql")
                create_submitted_defense = get_sql_by_path("tracker/sql/create_table_submitted_defense.sql")
                
                execute_sql(DB, create_hammers)
                execute_sql(DB, create_defense_calls)
                execute_sql(DB, create_submitted_defense)

                await message.channel.send(embed=response)
        
        elif command.startswith(Commands.Tracker.SET_ADMIN):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                server_role = " ".join(post[3:])

                if validate_role_exists(message.guild, server_role) is False:
                    response = invalid_role_error(server_role)
                    await message.channel.send(embed=response)
                    return

                try:
                    response = set_admin(self.config, guild_record[Config.ID], server_role)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([guild_record[Config.ADMIN_ROLE]])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Tracker.SET_USER):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                server_role = " ".join(post[3:])

                if validate_role_exists(message.guild, server_role) is False:
                    response = invalid_role_error(server_role)
                    await message.channel.send(embed=response)
                    return

                try:
                    response = set_user(self.config, str(message.guild.id), server_role)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([guild_record[Config.ADMIN_ROLE]])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Tracker.SET_SERVER):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                game_server = post[3]

                try:
                    response = set_game_server(self.config, str(message.guild.id), game_server)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([guild_record[Config.ADMIN_ROLE]])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Tracker.INFO):
            if user_has_role(guild_record[Config.ADMIN_ROLE], message):
                try:
                    guild_id = str(message.guild.id)
                    response = give_info(self.config, guild_id)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([guild_record[Config.ADMIN_ROLE]])
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Tracker.ADD):
            if user_has_role(guild_record[Config.ADMIN_ROLE], message):
                try:
                    post = message.content.split(" ")
                    validated = validate_add_input(post)
                    if validated:
                        DB = guild_record[Config.DATABASE]
                        coordinates = post.pop()
                        coordinates = coordinates.replace("/", "|")
                        link = post.pop()
                        ign = post[2:]
                        if len(ign) > 1:
                            ign = " ".join(ign).lower()
                        else:
                            ign = ign[0].lower()
                        unique = validate_unique_url(DB, link, ign)
                        if unique:
                            response = add_report(DB, ign, link, coordinates)
                        else:
                            response = not_unique_error()
                    else:
                        response = invalid_input_error()
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([guild_record[Config.ADMIN_ROLE]])
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Tracker.GET):
            if user_has_role(guild_record[Config.ADMIN_ROLE], message) or user_has_role(guild_record[Config.USER_ROLE], message):
                post = message.content.split(" ")
                
                DB = guild_record[Config.DATABASE]
                game_server = guild_record[Config.GAME_SERVER]

                try:
                    if isinstance(int(post[-1]), int):
                        response = get_reports(DB, " ".join(post[2:-1]), game_server, post[-1])
                except ValueError:
                    response = get_one_report(DB, " ".join(post[2:]), game_server)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([guild_record[Config.USER_ROLE], guild_record[Config.ADMIN_ROLE]])
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Tracker.DELETE):
            if user_has_role(guild_record[Config.ADMIN_ROLE], message):
                post = message.content.split(" ")
                ign = post[2]
                id = post[3]
                DB = guild_record[Config.DATABASE]
                response = delete_report(DB, ign, id)
            else:
                response = incorrect_roles_error([guild_record[Config.ADMIN_ROLE]])
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Tracker.LIST_ALL):
            if user_has_role(guild_record[Config.ADMIN_ROLE], message) or user_has_role(guild_record[Config.USER_ROLE], message):
                DB = guild_record[Config.DATABASE]

                response = list_all_names(DB)
            else:
                response = incorrect_roles_error([guild_record[Config.USER_ROLE], guild_record[Config.ADMIN_ROLE]])
            await message.channel.send(embed=response)
        
        elif command.startswith(Commands.Tracker.HELP):
            response = give_help()

            await message.channel.send(embed=response)

        elif command.startswith(Commands.General.DEV_INFO):
            print(message)
            print(message.guild.owner)

            await message.delete()

        elif command.startswith(Commands.General.GEAR):
            url = message.content.split(" ")[1]
            response = get_hero_items(url)

            await message.channel.send(embed=response)

        elif command.startswith(Commands.Defense.SET_ANVIL_ROLE):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                server_role = " ".join(post[4:])

                if validate_role_exists(message.guild, server_role) is False:
                    response = invalid_role_error(server_role)
                    await message.channel.send(embed=response)
                    return

                try:
                    response = set_anvil(self.config, str(message.guild.id), server_role)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([guild_record[Config.ADMIN_ROLE]])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Defense.SET_CHANNEL):
            if user_is_guild_admin(message):
                post = message.content.split(" ")
                channel_id = post[3]

                try:
                    response = set_defense_channel(self.config, str(message.guild.id), channel_id)
                except KeyError:
                    response = no_db_error()
            else:
                response = incorrect_roles_error([guild_record[Config.ADMIN_ROLE]])
            self.config.read("config.ini")
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Defense.LIST_OPEN):
            if user_has_role(guild_record[Config.ANVIL_ROLE], message) or user_is_guild_admin(message):
                DB = guild_record[Config.DATABASE]
                response = list_open_cfds(DB)
            else:
                response = incorrect_roles_error([guild_record[Config.USER_ROLE], guild_record[Config.ADMIN_ROLE]])
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Defense.SEND):
            if user_has_role(guild_record[Config.ANVIL_ROLE], message) or user_is_guild_admin(message):
                DB = guild_record[Config.DATABASE]
                post = message.content.split(" ")
                cfd_id = post[2]
                amount_sent = int(post[3].replace(",", ""))

                response = send_defense(f"databases/{guild_id}.db", cfd_id, amount_sent, message)
            else:
                response = incorrect_roles_error([guild_record[Config.ANVIL_ROLE]])
            await message.channel.send(embed=response)

        elif command.startswith(Commands.Defense.LEADERBOARD):
            if user_has_role(guild_record[Config.ANVIL_ROLE], message) or user_is_guild_admin(message):
                guild_id = str(message.guild.id)
                self.DB = self.config[guild_id]["database"]

                response = get_leaderboard(f"databases/{guild_id}.db")
            else:
                response = incorrect_roles_error([guild_record[Config.USER_ROLE], guild_record[Config.ADMIN_ROLE]])
            await message.channel.send(embed=response)
        else:
            return



    async def on_scheduled_event_create(self, event):
        # Refresh config
        self.config.read("config.ini")
        guild_id = str(event.guild.id)
        defense_channel = self.config[guild_id]["defense_channel"]
        game_server = self.config[guild_id]["game_server"]

        x, y = event.name.replace("/", "|").split("|")

        create_cfd(f"databases/{guild_id}.db", event.creator.id, event.id,
            event.creator.display_name, event.start_time, x, y, event.description)
        
        embed = discord.Embed(color=Colors.SUCCESS)
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

    async def on_scheduled_event_delete(self, event):
        # Refresh config
        self.config.read("config.ini")
        guild_id = str(event.guild.id)
        cancel_cfd(f"databases/{guild_id}.db", event.id)


client = Tracker(intents=intents)
client.run(client.TOKEN)
