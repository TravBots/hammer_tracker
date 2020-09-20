import os
import sqlite3
import discord
import configparser
import re

from funcs import *

config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['default']['token']
DB = config['default']['database']

client = discord.Client()

#error = 0xB22222
#success = 0x207325

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!tracker set admin ') and "tracker admin" in [a.name.lower() for a in message.author.roles]:
        post = message.content.split(" ")
        server_role = " ".join(post[3:])
        
        try:
            response = set_admin(str(message.guild.id), server_role)
        except KeyError:
            response = no_db_error()

        await message.channel.send(embed=response)

    elif message.content.startswith('!tracker set user ') and "tracker admin" in [a.name.lower() for a in message.author.roles]:
        post = message.content.split(" ")
        server_role = " ".join(post[3:])
        
        try:
            response = set_user(str(message.guild.id), server_role)
        except KeyError:
            response = no_db_error()

        await message.channel.send(embed=response)

    elif message.content.startswith('!tracker init') and "tracker admin" in [a.name.lower() for a in message.author.roles]:
        response = init(message)
        
        guild_id = str(message.guild.id)
        DB = config[guild_id]['database']
        create_table(DB)

        await message.channel.send(embed=response)

    elif message.content.startswith('!tracker info'):
        guild_id = str(message.guild.id)
        admin_role = config[guild_id]['admin_role']
        user_role = config[guild_id]['user_role']

        print(admin_role, user_role, message.author.roles)

        if admin_role.lower() in [a.name.lower() for a in message.author.roles]:
            try:
                guild_id = str(message.guild.id)
                print(guild_id)
                DB = config[guild_id]['database']
                print(DB)
                guild = str(message.guild.name)
                print(guild)
                response = give_info(DB, guild_id)
            except KeyError:
                response = no_db_error()

        await message.channel.send(embed=response)

    elif message.content.startswith('!tracker add '):
        guild_id = str(message.guild.id)
        admin_role = config[guild_id]['admin_role']
        user_role = config[guild_id]['user_role']

        if admin_role.lower() in [a.name.lower() for a in message.author.roles]:
            try:
                post = message.content.split(" ")
                validated = validate_add_input(post) 
                if validated:
                    guild_id = str(message.guild.id)
                    DB = config[guild_id]['database']
                    unique = validate_unique_url(DB, post[-1], " ".join((post[2:-1])))
                    if unique:
                        response = add_report(DB, " ".join(post[2:-1]), post[-1])
                    else:
                        response = not_unique_error()
                else:
                    response = no_link_error()
            except KeyError:
                response = no_db_error()
        
        await message.channel.send(embed=response)

    elif message.content.startswith('!tracker get '):
        guild_id = str(message.guild.id)
        admin_role = config[guild_id]['admin_role'].lower()
        user_role = config[guild_id]['user_role'].lower()
        roles = [admin_role, user_role]

        if admin_role in [a.name.lower() for a in message.author.roles] or user_role in [a.name.lower() for a in message.author.roles]:
            post = message.content.split(" ")
            DB = config[guild_id]['database']
            
            try:
                if isinstance(int(post[-1]), int):    
                    response = get_reports(DB, " ".join(post[2:-1]), post[-1])
            except ValueError:
                response = get_one_report(DB, " ".join(post[2:]))
            except KeyError:
                response = no_db_error()

        await message.channel.send(embed=response)
    
    elif message.content.startswith('!tracker list all'):
        guild_id = str(message.guild.id)
        admin_role = config[guild_id]['admin_role'].lower()
        user_role = config[guild_id]['user_role'].lower()
        
        if user_role in [a.name.lower() for a in message.author.roles] or admin_role in [a.name.lower() for a in message.author.roles]:
            guild_id = str(message.guild.id)
            DB = config[guild_id]['database']

            response = list_all_names(DB)

        await message.channel.send(embed=response)

    elif message.content.startswith('!tracker'):
        guild_id = str(message.guild.id)
        admin_role = config[guild_id]['admin_role'].lower()
        user_role = config[guild_id]['user_role'].lower()
        
        if user_role in [a.name.lower() for a in message.author.roles] or admin_role in [a.name.lower() for a in message.author.roles]:
            response = give_help()

        await message.channel.send(embed=response)
    
    elif message.content.startswith('!dev info'):
        print(message)
        print(message.guild.owner)

        await message.delete()
    
    else:
        return

client.run(TOKEN)
