import sqlite3

import discord
from utils.constants import BOT_SERVERS_DB_PATH, GAME_SERVERS_DB_PATH, Colors
from utils.logger import logger


def init(config, message):
    guild_name = str(message.guild.name)
    guild_id = str(message.guild.id)
    message_author = str(message.author)

    if not config.has_section(guild_id):
        config.add_section(guild_id)
        config[guild_id]["init_user"] = message_author

    # `database` and `server` should be able to be updated. `init_user` above should not.
    config[guild_id]["database"] = f"{BOT_SERVERS_DB_PATH}{guild_id}.db"
    config[guild_id]["server"] = guild_name

    with open("config.ini", "w") as conf:
        config.write(conf)

    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(name="Success", value="Database initialized")

    return embed


def get_sql_by_path(path):
    with open(path, "r") as sql_file:
        sql = sql_file.read()

    return sql


def execute_sql(db_name, sql):
    conn = sqlite3.connect(db_name)
    logger.info(f"Running sql:\n{sql}")
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
    logger.info(f"Executing query: {query}")
    deleted_rows = conn.execute(
        query,
        (
            id,
            ign.lower(),
        ),
    )

    for row in deleted_rows:
        logger.info(row)

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


def get_thread_from_id(guild: discord.Guild, thread_id: str):
    return guild.get_thread(int(thread_id))


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
        ) VALUES (?,?,?,?,?,?,?,CURRENT_TIMESTAMP) RETURNING *;
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

    cfd = conn.execute(query, data)
    id = cfd.fetchone()[0]
    conn.commit()
    conn.close()

    return id


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


def insert_defense_thread(db_name, defense_thread_id, cfd_id, name, jump_url):
    conn = sqlite3.connect(db_name)

    query = "INSERT INTO DEFENSE_THREADS (id,defense_call_id,name,jump_url) VALUES (?,?,?,?);"
    data = (defense_thread_id, cfd_id, name, jump_url)

    conn.execute(query, data)
    conn.commit()
    logger.info(
        f"Inserted record into DEFENSE_THREADS:\n{defense_thread_id}\n({cfd_id}\n{name}\n{jump_url})"
    )
    conn.close()


def list_open_cfds(db_name, game_server):
    conn = sqlite3.connect(db_name)
    query = conn.execute(
        """
        select
            dc.id,
            datetime(dc.land_time, 'localtime'),
            dc.x_coordinate,
            dc.y_coordinate,
            dc.amount_requested,
            dc.amount_submitted,
            dt.jump_url
        from defense_calls dc
        join defense_threads dt
            on dc.id = dt.defense_call_id
        where current_timestamp < land_time
        and not cancelled;
        """
    )

    response = []
    for row in query:
        id = row[0]
        land_time = row[1]
        x_coordinate = row[2]
        y_coordinate = row[3]
        amount_requested = row[4]
        amount_submitted = row[5]
        jump_url = row[6]
        values = f"""
        **ID: {id}**
        Land Time:\n{str(land_time).split(".")[0]}
        Thread: {jump_url}
        Location: [{x_coordinate}|{y_coordinate}]({game_server}/position_details.php?x={x_coordinate}&y={y_coordinate})
        Requested: {amount_requested:,}
        Submitted: {amount_submitted:,}
        Remaining: __{amount_requested - amount_submitted:,}__
        """
        response.append(values)

    if len(response) > 0:
        embed = discord.Embed(title="Open Defense Calls", color=Colors.SUCCESS)

        max_size = 6000
        cumulative_size = len(embed.title)

        for index, cfd in enumerate(response):
            logger.info(f"Cumulative size: {cumulative_size}")
            cumulative_size += len(cfd)
            if cumulative_size < max_size:
                embed.add_field(
                    name="\u200b",  # You can't have an empty name
                    value=response[index],
                    inline=True,
                )
            else:
                logger.warn(
                    f"Error: Embed total size would be {cumulative_size} characters"
                )
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
        WHERE id = ? returning amount_requested, amount_submitted;
        """
    logger.info(f"Executing query: {query}")
    try:
        sent_def = conn.execute(
            query,
            (amount_sent, cfd_id),
        )

        sent_def = sent_def.fetchone()
        amount_requested = sent_def[0]
        amount_submitted = sent_def[1]
        logger.info(amount_requested, amount_submitted)

        conn.commit()
    except TypeError:
        """TypeError if the provided CFD ID doesn't exist, as sent_def is then None,
        which is not subscriptable. The error is on: amount_requested = sent_def[0]"""
        conn.close()

        embed = discord.Embed(color=Colors.ERROR)
        embed.add_field(
            name="Invalid CFD",
            value=f"The CFD with ID {cfd_id} does not exist. Try `!def list` to see open CFDs.",
        )

        return embed

    conn = sqlite3.connect(db_name)
    query = """
        INSERT INTO SUBMITTED_DEFENSE (
        defense_call_id,
        submitted_by_id,
        submitted_by_name,
        amount_submitted
        ) VALUES (?,?,?,?);
        """
    logger.info(f"Executing query: {query}")
    conn.execute(
        query,
        (cfd_id, message.author.id, message.author.name, amount_sent),
    )

    conn.commit()

    embed = discord.Embed(color=Colors.WARNING)
    embed.add_field(
        name="Confirmed",
        value=f"{amount_sent:,} defense registered for CFD with ID {cfd_id}.\n**{amount_requested-amount_submitted:,} remaining**",
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
    logger.info(f"Executing query: {query}")
    rows = conn.execute(
        query,
        # (amount_sent, cfd_id),
    )

    conn.commit()

    result = ""

    for index, row in enumerate(rows):
        result += f"{index}. <@{row[0]}> ({row[1]:,})\n"
    embed = discord.Embed(color=Colors.SUCCESS)
    embed.add_field(
        name="Leaderboard",
        value=result,
    )

    conn.close()

    return embed


def process_name(x):
    first_part = str(x).split(" ")[0].strip(".")
    if first_part.isnumeric():
        logger.info(f"logging x: {x}. stripped: {str(x).replace('.', '')}")
        return str(x).replace(".", "")
    return x

def get_connection_path(config) -> str:
    path = f"{GAME_SERVERS_DB_PATH}"

    game_server = config["game_server"]

    server_number, speed, domain = game_server.split(".")[0:3]
    server_number = server_number.split("ts")[1]

    domains = {
        "america": "am",
        "europe": "eu",
        "arabics": "arab"
    }
    # if game_server == "https://ts3.x1.america.travian.com":
    #     path += "am3.db"
    # elif game_server == "https://ts2.x1.america.travian.com":
    #     path += "am2.db"

    database_name = f"{domains[domain]}{server_number}.db"
    logger.debug(f"database_name: {database_name}")
    return path+database_name


def get_alliance_tag_from_id(conn, alliance_id):
    query = "select alliance_name from v_alliance_lookup where alliance_id = ?"
    logger.info(f"Executing query: {query}")
    result = conn.execute(query, (alliance_id,)).fetchone()
    if result:
        return result[0]
    return None
