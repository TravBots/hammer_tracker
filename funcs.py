import os
import sqlite3
import discord
import configparser
import re

config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['default']['token']
DB = config['default']['database']

#client = discord.Client()

error = 0xB22222
success = 0x207325

def init(message):
    guild_name = str(message.guild.name)
    guild_id = str(message.guild.id)
    message_author = str(message.author)

    try:
        print(guild_name, guild_id)
        config.add_section(guild_id)
        config[guild_id]['database'] = 'databases/{}.db'.format(guild_id)
        config[guild_id]['server'] = guild_name
        config[guild_id]['init_user'] = message_author

        with open('config.ini', 'w') as conf:
            config.write(conf)
        
        embed = discord.Embed(color=success)
        embed.add_field(name="Success", value="Database initialized")
    except configparser.DuplicateSectionError:
        embed = discord.Embed(color=error)
        embed.add_field(name="Error", value="Database already exists")

    return embed

def set_admin(guild_id, server_role):
    config[guild_id]["admin_role"] = server_role

    with open('config.ini', 'w') as conf:
        config.write(conf)
    
    embed = discord.Embed(color=success)
    embed.add_field(name="Success", value="Role {} set as Tracker Admin".format(server_role))

    return embed

def set_user(guild_id, server_role):
    config[guild_id]["user_role"] = server_role

    with open('config.ini', 'w') as conf:
        config.write(conf)

    embed = discord.Embed(color=success)
    embed.add_field(name="Success", value="Role {} set as Tracker User".format(server_role))

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

def validate_unique_url(db_name, url, ign):
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
    
    print(db_name, url, urls, unique, ign)
    return unique

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

def list_all_names(db_name):
    conn = sqlite3.connect(db_name)
    query = conn.execute('''select distinct IGN, datetime(max(timestamp), '-4 hours') from hammers group by 1 order by 1''')

    try:
        response = ''
        for row in query:
            print(row)
            response += "\n{} | {}".format(row[0], row[1])
        embed = discord.Embed(title="Recorded Hammers", color=success)
        embed.add_field(name="Player   |   Timestamp", value=response)
    except:
        print("Error")

    conn.close()

    return embed

def give_help():
    embed = discord.Embed(description="Help", color=success)
    embed.add_field(name="List IGNs in Database [Tracker User]", value="`!tracker list all`")
    embed.add_field(name="Get Reports [Tracker User]", value="`!tracker get <IGN> <NUMBER - Optional>`")
    embed.add_field(name="Add a Report [Tracker Admin]", value="`!tracker add <IGN> <LINK>`")
    embed.add_field(name="Initialize Database [Tracker Admin]", value="`!tracker init`")
    embed.add_field(name="Get Tracker Information [Tracker Admin]", value="`!tracker info`")

    return embed

def give_info(db_name, guild_id):
    embed = discord.Embed(description="Information", color=success)
    embed.add_field(name="Server Name:", value=config[guild_id]["server"])
    embed.add_field(name="Database Name:", value=db_name)
    embed.add_field(name="Tracker Admin", value=config[guild_id]["admin_role"])
    embed.add_field(name="Tracker User", value=config[guild_id]["user_role"])


    return embed

def no_db_error():
    embed = discord.Embed(color=error)
    embed.add_field(name="Error", value="Database not initialized. Try `!tracker init` first")

    return embed

def no_link_error():
    embed = discord.Embed(color=error)
    embed.add_field(name="Error", value="No link provided. See `!tracker help` for syntax help")
    
    return embed

def not_unique_error():
    embed = discord.Embed(color=error)
    embed.add_field(name="Error", value="This report has already been recorded")

    return embed

