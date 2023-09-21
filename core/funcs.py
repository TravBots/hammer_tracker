import sqlite3
import discord
import configparser

from constants import Colors


def init(config, message):
    guild_name = str(message.guild.name)
    guild_id = str(message.guild.id)
    message_author = str(message.author)

    print(config.sections())
    try:
        print(guild_name, guild_id)
        config.add_section(guild_id)
        config[guild_id]["database"] = "databases/{}.db".format(guild_id)
        config[guild_id]["server"] = guild_name
        config[guild_id]["init_user"] = message_author

        with open("config.ini", "w") as conf:
            config.write(conf)

        embed = discord.Embed(color=Colors.SUCCESS)
        embed.add_field(name="Success", value="Database initialized")
    except configparser.DuplicateSectionError:
        embed = discord.Embed(color=Colors.ERROR)
        embed.add_field(name="Error", value="Database already exists")

    return embed


def set_admin(config, guild_id, server_role):
    config[guild_id]["admin_role"] = server_role

    with open("config.ini", "w") as conf:
        config.write(conf)

    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Success", value="Role {} set as Tracker Admin".format(server_role)
    )

    return embed


def set_user(config, guild_id, server_role):
    config[guild_id]["user_role"] = server_role

    with open("config.ini", "w") as conf:
        config.write(conf)

    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Success", value="Role {} set as Tracker User".format(server_role)
    )

    return embed


def set_anvil(config, guild_id, server_role):
    config[guild_id]["anvil_role"] = server_role

    with open("config.ini", "w") as conf:
        config.write(conf)

    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Success", value="Role {} set as Anvil Role".format(server_role)
    )

    return embed


def set_game_server(config, guild_id, game_server):
    config[guild_id]["game_server"] = game_server

    with open("config.ini", "w") as conf:
        config.write(conf)

    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Success", value="Game server was set as {}".format(game_server)
    )

    return embed


def set_defense_channel(config, guild_id, defense_channel_id):
    config[guild_id]["defense_channel"] = defense_channel_id

    with open("config.ini", "w") as conf:
        config.write(conf)

    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Success", value="Defense Channel was set as {}".format(defense_channel_id)
    )

    return embed


def get_sql_by_path(path):
    with open(path, "r") as sql_file:
        sql = sql_file.read()

    return sql


def execute_sql(db_name, sql):
    conn = sqlite3.connect(db_name)
    print(f"Running sql:\n{sql}")
    conn.execute(sql)
    conn.commit()
    conn.close()


def add_report(db_name, ign, link, coordinates):
    conn = sqlite3.connect(db_name)

    query = "INSERT INTO HAMMERS (IGN,LINK,TIMESTAMP, COORDINATES) VALUES (?, ?, CURRENT_TIMESTAMP, ?);"
    data = (ign, link, coordinates)

    conn.execute(query, data)
    conn.commit()
    conn.close()

    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Success", value="Report for player {} added to database".format(ign)
    )

    return embed


def get_reports(db_name, ign, game_server, count="1"):
    conn = sqlite3.connect(db_name)
    query = conn.execute(
        """select ID, IGN, LINK, COORDINATES, datetime(TIMESTAMP, '-4 hours') from hammers where lower(ign) = ? order by timestamp limit ?;""",
        (ign.lower(), count),
    )

    response = ""
    for row in query:
        id = row[0]
        ign = row[1]
        link = row[2]
        coordinates = row[3]
        split_coordinates = coordinates.split("|")
        x, y = split_coordinates[0], split_coordinates[1]
        map_link = f"[{x}|{y}]({game_server}/position_details.php?x={x}&y={y})"
        timestamp = row[4]

        response += "\nID: {} \nReport: {} \nCoordinates: {} \nTimestamp: {}\n".format(
            id, link, map_link, timestamp
        )

    if response != "":
        embed = discord.Embed(
            title="Reports for player {}".format(ign),
            description="Most recent reports at the bottom",
            color=Colors.SUCCESS,
        )
        embed.add_field(name="Reports", value=response)
    else:
        embed = discord.Embed(color=Colors.ERROR)
        embed.add_field(
            name="Error",
            value="No entries for the player {} in the database".format(ign),
        )

    conn.close()

    return embed


def get_one_report(db_name, ign, game_server):
    conn = sqlite3.connect(db_name)
    query = conn.execute(
        """select ID, IGN, LINK, COORDINATES, datetime(TIMESTAMP, '-4 hours') from hammers where lower(ign) = ? order by timestamp desc limit 1;""",
        (ign.lower(),),
    )

    response = ""
    for row in query:
        id = row[0]
        ign = row[1]
        link = row[2]
        coordinates = row[3]
        split_coordinates = coordinates.split("|")
        x, y = split_coordinates[0], split_coordinates[1]
        map_link = f"[{x}|{y}]({game_server}/position_details.php?x={x}&y={y})"
        timestamp = row[4]
        response += "ID: {} \nReport: {} \nCoordinates: {} \nTimestamp: {}\n".format(
            id, link, map_link, timestamp
        )

    if response != "":
        embed = discord.Embed(
            title="Latest report for player {}".format(ign), color=Colors.SUCCESS
        )
        embed.add_field(name="Report", value=response)
    else:
        embed = discord.Embed(color=Colors.ERROR)
        embed.add_field(
            name="Error", value="No entry for the player {} in the database".format(ign)
        )

    conn.close()

    return embed


def delete_report(db_name, ign, id):
    conn = sqlite3.connect(db_name)
    query = """
        delete from hammers where ID = ? and IGN = ? returning *;
        """
    print(f"Executing query: {query}")
    deleted_rows = conn.execute(
        query,
        (
            id,
            ign.lower(),
        ),
    )

    for row in deleted_rows:
        print(row)

    conn.commit()

    embed = discord.Embed(color=Colors.WARNING)
    embed.add_field(
        name="Confirmed", value=f"Deleted report for player {ign} with ID {id}"
    )

    conn.close()

    return embed


def list_all_names(db_name):
    conn = sqlite3.connect(db_name)
    query = conn.execute(
        """select IGN, COORDINATES, datetime(max(timestamp), '-4 hours') from hammers group by 1,2 order by 1,3"""
    )

    response = ""
    for row in query:
        ign = row[0]
        coordinates = row[1]
        timestamp = row[2]
        response += "\n{} | {} | {}".format(ign, coordinates, timestamp)

    if response != "":
        embed = discord.Embed(title="Recorded Hammers", color=Colors.SUCCESS)
        embed.add_field(name="Player   |   Coordinates   |   Last Seen", value=response)
    else:
        embed = discord.Embed(color=Colors.ERROR)
        embed.add_field(name="Error", value="No entries found in the database")
    conn.close()

    return embed


def give_help():
    embed = discord.Embed(description="Help", color=Colors.SUCCESS)
    embed.add_field(
        name="List IGNs in Database [Tracker User]", value="`!tracker list all`"
    )
    embed.add_field(
        name="Get Reports [Tracker User]",
        value="`!tracker get <IGN> <NUMBER - Optional>`",
    )
    embed.add_field(
        name="Add a Report [Tracker Admin]",
        value="`!tracker add <IGN> <LINK> <COORDINATES>`",
    )
    embed.add_field(
        name="Delete a Report [Tracker Admin]",
        value="`!tracker delete <IGN> <REPORT ID>`",
    )
    embed.add_field(name="Initialize Database [Tracker Admin]", value="`!tracker init`")
    embed.add_field(
        name="Get Tracker Information [Tracker Admin]", value="`!tracker info`"
    )
    embed.add_field(
        name="Set Tracker Admin [Tracker Admin]",
        value="`!tracker set admin <ROLE NAME>`",
    )
    embed.add_field(
        name="Set Tracker User [Tracker Admin]", value="`!tracker set user <ROLE NAME>`"
    )

    return embed


def give_info(config, guild_id):
    embed = discord.Embed(description="Information", color=Colors.SUCCESS)
    embed.add_field(name="Server Name:", value=config[guild_id]["server"])
    embed.add_field(name="Game Server", value=config[guild_id]["game_server"])
    embed.add_field(name="Database Name:", value=config[guild_id]["database"])
    embed.add_field(name="Tracker Admin", value=config[guild_id]["admin_role"])
    embed.add_field(name="Tracker User", value=config[guild_id]["user_role"])

    return embed


def get_channel_from_id(guild: discord.Guild, channel_id: str):
    return guild.get_channel(int(channel_id))


def create_cfd(
    db_name,
    created_by_id,
    event_id,
    created_by_name,
    land_time,
    x_coordinate,
    y_coordinate,
    amount_requested,
):
    conn = sqlite3.connect(db_name)

    query = """
    INSERT INTO DEFENSE_CALLS (
        created_by_id,
        event_id,
        created_by_name,
        land_time, 
        x_coordinate, 
        y_coordinate, 
        amount_requested, 
        created_at
        ) VALUES (?,?,?,?,?,?,?,CURRENT_TIMESTAMP);
    """
    data = (
        created_by_id,
        event_id,
        created_by_name,
        land_time,
        x_coordinate,
        y_coordinate,
        amount_requested.replace(",", ""),
    )

    conn.execute(query, data)
    conn.commit()
    conn.close()


def cancel_cfd(db_name, event_id):
    conn = sqlite3.connect(db_name)

    query = """
    UPDATE DEFENSE_CALLS
    SET CANCELLED = TRUE
    WHERE event_id = ? RETURNING *;
    """
    data = (event_id,)

    conn.execute(query, data)
    conn.commit()
    conn.close()


def list_open_cfds(db_name):
    conn = sqlite3.connect(db_name)
    query = conn.execute(
        """
        select 
            id, 
            datetime(land_time, '-4 hours'), 
            x_coordinate, 
            y_coordinate, 
            amount_requested, 
            amount_submitted 
        from defense_calls 
        where current_timestamp < land_time
        and amount_submitted < amount_requested
        and not cancelled;
        """
    )

    response = ""
    for row in query:
        id = row[0]
        land_time = row[1]
        x_coordinate = row[2]
        y_coordinate = row[3]
        amount_requested = row[4]
        amount_submitted = row[5]
        values = {
            "ID": str(id),
            "Land Time": str(land_time).split(".")[0],
            "X-Coordinate": str(x_coordinate),
            "Y-Coordinate": str(y_coordinate),
            "Amount Requested": str(f"{amount_requested:,}"),
            "Amount Submitted": str(f"{amount_submitted:,}"),
            "Amount Remaining": str(f"{amount_requested - amount_submitted:,}"),
        }
        for k, v in values.items():
            response += f"**{k}**: {v}\n"
        response += "\n"

    if response != "":
        embed = discord.Embed(title="Open Defense Calls", color=Colors.SUCCESS)
        embed.add_field(name="Defense Calls", value=response)
    else:
        embed = discord.Embed(color=Colors.SUCCESS)
        embed.add_field(name="All Clear", value="No open CFDs")
    conn.close()

    return embed


def send_defense(db_name, cfd_id: int, amount_sent: int, message: discord.Message):
    conn = sqlite3.connect(db_name)
    query = """
        UPDATE DEFENSE_CALLS
        SET amount_submitted = amount_submitted + ? 
        WHERE id = ? returning *;
        """
    print(f"Executing query: {query}")
    conn.execute(
        query,
        (amount_sent, cfd_id),
    )

    conn.commit()

    conn = sqlite3.connect(db_name)
    query = """
        INSERT INTO SUBMITTED_DEFENSE (
        defense_call_id,
        submitted_by_id,
        submitted_by_name,
        amount_submitted
        ) VALUES (?,?,?,?);
        """
    print(f"Executing query: {query}")
    conn.execute(
        query,
        (cfd_id, message.author.id, message.author.name, amount_sent),
    )

    conn.commit()

    embed = discord.Embed(color=Colors.WARNING)
    embed.add_field(
        name="Confirmed",
        value=f"{amount_sent} defense registered for CFD with ID {cfd_id}",
    )

    conn.close()

    return embed


def get_leaderboard(db_name):
    conn = sqlite3.connect(db_name)
    query = """
        select
            submitted_by_id,
            sum(amount_submitted)
        from SUBMITTED_DEFENSE
        group by 1
        order by 2 desc 
        limit 10;
        """
    print(f"Executing query: {query}")
    rows = conn.execute(
        query,
        # (amount_sent, cfd_id),
    )

    conn.commit()

    result = ""

    for index, row in enumerate(rows):
        result += f"{index}. <@{row[0]}> ({row[1]})\n"
    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Leaderboard",
        value=result,
    )

    conn.close()

    return embed