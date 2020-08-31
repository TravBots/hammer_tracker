import os
import sqlite3
import discord
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['default']['token']
DB = config['default']['database']

client = discord.Client()

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

    embed = discord.Embed(color=0x00ff00)
    embed.add_field(name="Success", value="Report for player {} added to database".format(ign))

    return embed

def get_report(db_name, ign, count):
    conn = sqlite3.connect(db_name)
    query = conn.execute('''select * from hammers where lower(ign) = ? order by timestamp limit ?;''', (ign.lower(), count))
    
    
    response = ''
    for row in query:
        response += "\nIGN: {} \nReport: {} \nTimestamp: {} \n".format(row[1], row[2], row[3])
    
    embed = discord.Embed(description="Most recent reports at the bottom", color=0x00ff00)
    embed.add_field(name="Reports", value=response)
    conn.close()
    return embed

def give_help():
    embed = discord.Embed(description="Help", color=0x00ff00)
    embed.add_field(name="Add a Report", value="!tracker add <IGN> <LINK>")
    embed.add_field(name="Get Reports", value="!tracker get <IGN> <NUMBER - Optional>")

    return embed

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith( '!tracker add'):
        post = message.content.split(" ")
        
        create_table("as3.db")
        response = add_report("as3.db", post[2], post[3])
        
        await message.channel.send(embed=response)

    if message.content.startswith('!tracker get'):
        post = message.content.split(" ")
        
        try:
            response = get_report("as3.db", post[2], post[3])
        except IndexError:
            response = get_report("as3.db", post[2], "1")
        
        await message.channel.send(embed=response)
    
    elif message.content.startswith('!tracker'):
        response = give_help()

        await message.channel.send(embed=response)
client.run(TOKEN)
