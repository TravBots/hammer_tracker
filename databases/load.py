#!/projects/hammer_tracker/dash_site/env/bin/python3
import sqlite3

import requests
from servers import SERVER_LINKS

with open("sql/replace_x_world.sql", "r") as sql_file:
    replace_x_world = sql_file.read()

with open("sql/insert_map_history.sql", "r") as sql_file:
    insert_map_history = sql_file.read()

for server in SERVER_LINKS:
    server_link = server[0]
    server_nick = server[1]

    try:
        print(f"Loading {server_link} into x_world")
        data = requests.get(server_link + "/map.sql")
        cnx = sqlite3.connect(f"game_servers/{server_nick}.db")
        cnx.executescript(replace_x_world)

        records = 0
        for record in data.text.split("\n"):
            cnx.execute(record)
            records += 1
        print(f"Loaded {records} into {server_nick}.db")
        cnx.commit()

        print(f"Updating history table for {server_link}\n")
        cnx.executescript(insert_map_history)
        cnx.commit()

        cnx.close()

    except Exception as e:
        print(f"Failed to collect map data for {server_link}\n{e}")
