import os
import sqlite3
import discord
import configparser
import re

config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['default']['token']
DB = config['default']['database']

client = discord.Client()

error = 0xB22222
success = 0x207325

def init(message):
    guild_name = str(message.guild.name)
    guild_id = str(message.guild.id)
    
    try:
        print(guild_name, guild_id)
        config.add_section(guild_id)
        config[guild_id]['database'] = 'databases/{}.db'.format(guild_id)

        with open('config.ini', 'w') as conf:
            config.write(conf)
        
        embed = discord.Embed(color=success)
        embed.add_field(name="Success", value="Database initialized")
    except configparser.DuplicateSectionError:
        embed = discord.Embed(color=error)
        embed.add_field(name="Error", value="Database already exists")

    return embed

def create_table(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute('''CREATE TABLE IF NOT EXISTS HAMMERS
        (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        IGN TEXT NOT NULL,
        LINK TEXT NOT NULL,
        TIMESTAMP TIMESTAMP NOT NULL);''')
    conn.commit()
    conn.close()

def add_report(db_name, ign, link):
    conn = sqlite3.connect(db_name)

    query = "INSERT INTO HAMMERS (IGN,LINK,TIMESTAMP) VALUES (?, ?, CURRENT_TIMESTAMP);"
    data = (ign, link)

    conn.execute(query, data)
    conn.commit()
    conn.close()

    embed = discord.Embed(color=success)
    embed.add_field(name="Success", value="Report for player {} added to database".format(ign))

    return embed

def validate_add_input(txt):
    pattern = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    url = [bool(re.search(pattern, part)) for part in txt]

    if url[-1] is True:
        return True
    else:
        return False

def get_reports(db_name, ign, count = "1"):
    conn = sqlite3.connect(db_name)
    query = conn.execute('''select IGN, LINK, datetime(TIMESTAMP, '-4 hours') from hammers where lower(ign) = ? order by timestamp limit ?;''', (ign.lower(), count))
    
    try: 
        response = ''
        for row in query:
            print(row)
            response += "\nReport: {} \nTimestamp: {} \n".format(row[1], row[2])

        embed = discord.Embed(title="Reports for player {}".format(row[0]), description="Most recent reports at the bottom", color=success)
        embed.add_field(name="Reports", value=response)
    except UnboundLocalError:
        embed = discord.Embed(color=error)
        embed.add_field(name="Error", value="No entry for the player {} in the database".format(ign))
    
    conn.close()
    
    return embed

def get_one_report(db_name, ign):
    conn = sqlite3.connect(db_name)
    query = conn.execute('''select IGN, LINK, datetime(TIMESTAMP, '-4 hours') from hammers where lower(ign) = ? order by timestamp desc limit 1;''', (ign.lower(),))

    try:
        response = ''
        for row in query:
            response += "\nReport: {} \nTimestamp: {}\n".format(row[1], row[2])

        embed = discord.Embed(title="Latest report for player {}".format(row[0]), color=success)
        embed.add_field(name="Report", value=response)
    except UnboundLocalError:
        embed = discord.Embed(color=error)
        embed.add_field(name="Error", value="No entry for the player {} in the database".format(ign))

    conn.close()

    return embed

def give_help():
    embed = discord.Embed(description="Help", color=success)
    embed.add_field(name="Add a Report [Tracker Admin]", value="`!tracker add <IGN> <LINK>`")
    embed.add_field(name="Get Reports [Tracker User]", value="`!tracker get <IGN> <NUMBER - Optional>`")
    embed.add_field(name="Initialize Database [Tracker Admin]", value="`!tracker init`")
    embed.add_field(name="Get Tracker Information [Tracker Admin]", value="`!tracker info`")

    return embed

def give_info(db_name, guild_name):
    embed = discord.Embed(description="Information", color=success)
    embed.add_field(name="Server Name:", value=guild_name)
    embed.add_field(name="Database Name:", value=db_name)

    return embed

def no_db_error():
    embed = discord.Embed(color=error)
    embed.add_field(name="Error", value="Database not initialized. Try `!tracker init` first")

    return embed

def no_link_error():
    embed = discord.Embed(color=error)
    embed.add_field(name="Error", value="No link provided. See `!tracker help` for syntax help")
    
    return embed

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!tracker init') and "tracker admin" in [a.name.lower() for a in message.author.roles]:
        response = init(message)
        
        guild_id = str(message.guild.id)
        DB = config[guild_id]['database']
        create_table(DB)

        await message.channel.send(embed=response)
    
    elif message.content.startswith('!tracker info') and "tracker admin" in [a.name.lower() for a in message.author.roles]:
        try:
            guild_id = str(message.guild.id)
            DB = config[guild_id]['database']
            guild = str(message.guild.name)
            response = give_info(DB, guild)
        except KeyError:
            response = no_db_error()

        await message.channel.send(embed=response)

    elif message.content.startswith('!tracker add') and "tracker admin" in [a.name.lower() for a in message.author.roles]:
        try:
            post = message.content.split(" ")
            validated = validate_add_input(post)
            
            if validated:
                guild_id = str(message.guild.id)
                DB = config[guild_id]['database']
                response = add_report(DB, " ".join(post[2:-1]), post[-1])
            else:
                response = no_link_error()
        except KeyError:
            response = no_db_error()

        await message.channel.send(embed=response)

    elif message.content.startswith('!tracker get') and ("tracker user" in [a.name.lower() for a in message.author.roles] or "tracker admin" in [a.name.lower() for a in message.author.roles]):
        post = message.content.split(" ")
        guild_id = str(message.guild.id)
        DB = config[guild_id]['database']
        
        try:
            if isinstance(int(post[-1]), int):    
                response = get_reports(DB, " ".join(post[2:-1]), post[-1])
        except ValueError:
            response = get_one_report(DB, " ".join(post[2:]))
        except KeyError:
            response = no_db_error()

        await message.channel.send(embed=response)
    
    elif message.content.startswith('!tracker') and ("tracker user" in [a.name.lower() for a in message.author.roles] or "tracker admin" in [a.name.lower() for a in message.author.roles]):
        response = give_help()

        await message.channel.send(embed=response)

    else:
        return

client.run(TOKEN)
