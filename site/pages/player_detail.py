import sqlite3

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, dash_table
from datetime import datetime, timedelta

dash.register_page(__name__, path_template="/players/<player_id>")


def pop_table(player_id, cnx):
    village_pop_query = f"select * from v_seven_day_pop where player_id = {player_id};"
    print(village_pop_query)

    df = pd.read_sql_query(village_pop_query, cnx)
    working_date = datetime.strptime(df["load_date"][0], "%Y-%m-%d")

    df = add_total_row(df)
    add_pop_diff_markdown(df)

    pop_table = dash_table.DataTable(
        columns=[
            {
                "name": "Village Name",
                "id": "village_name",
                "type": "text",
                "presentation": "markdown",
            },
            {
                "name": "Founded",
                "id": "founded",
                "type": "text",
                "presentation": "markdown",
            },
            {
                "name": (working_date).strftime("%m-%d"),
                "id": "today",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": (working_date - timedelta(days=1)).strftime("%m-%d"),
                "id": "yesterday",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": (working_date - timedelta(days=2)).strftime("%m-%d"),
                "id": "two_days_ago",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": (working_date - timedelta(days=3)).strftime("%m-%d"),
                "id": "three_days_ago",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": (working_date - timedelta(days=4)).strftime("%m-%d"),
                "id": "four_days_ago",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": (working_date - timedelta(days=5)).strftime("%m-%d"),
                "id": "five_days_ago",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": (working_date - timedelta(days=6)).strftime("%m-%d"),
                "id": "six_days_ago",
                "type": "numeric",
                "presentation": "markdown",
            },
        ],
        data=df.to_dict("records"),
        style_table={
            "width": "90%",
        },
        style_data={
            "width": "150px",
            "minWidth": "50px",
            "maxWidth": "200px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        style_cell_conditional=[
            {"if": {"column_id": c}, "textAlign": "left"}
            for c in ["village_name", "founded"]
        ],
        markdown_options={"link_target": "_self", "html": True},
        sort_action="native",
    )

    return pop_table


def layout(player_id=None):
    cnx = sqlite3.connect("../databases/game_servers/am3.db")
    # TODO: Pass player_id as a param instead of f-string. This is insecure.
    query = f"select strftime('%Y-%m-%d', datetime(inserted_at, 'unixepoch', 'localtime')) as date, player_id, sum(population) as population from map_history where player_id = {player_id} group by 1,2 order by 1;"
    history = pd.read_sql_query(query, cnx)
    query = f"select player_name, sum(population) as population from x_world where player_id = {player_id} group by 1"
    player = pd.read_sql_query(query, cnx)

    ref = max(0, len(history) - 8)
    fig = go.Figure(
        go.Indicator(
            mode="number+delta",
            value=history["population"][len(history) - 1],
            delta={
                "reference": history["population"][ref],
                "valueformat": ".0f",
            },
            title={"text": f"{player['player_name'][0]} (7 day diff)"},
            domain={"y": [0, 1], "x": [0.25, 0.75]},
        )
    )
    fig.add_trace(
        go.Scatter(y=history["population"], x=history["date"], name="Population")
    )

    query = f"""
    SELECT
        x_coordinate as 'X Coordinate',
        y_coordinate as 'Y Coordinate',
        alliance_tag as 'Alliance Name',
        player_name as 'Player Name',
        village_name as 'Village Name',
        case
            when tribe_id = 1 then 'Roman'
            when tribe_id = 2 then 'Teuton'
            when tribe_id = 3 then 'Gaul'
        end as 'Tribe',
        population as 'Population',
        capital as 'Capital?'
    FROM x_world where player_id = {player_id}
    order by player_name;"""

    data = pd.read_sql_query(query, cnx)
    map = px.scatter(
        data_frame=data,
        x="X Coordinate",
        y="Y Coordinate",
        color="Player Name",
        hover_data=["Player Name", "Village Name", "Tribe", "Population", "Capital?"],
        width=1100,
        height=1000,
    )

    map.update_xaxes(range=[-200, 200])
    map.update_yaxes(range=[-200, 200])
    map.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    map.update_traces(marker={"size": 7})

    map.add_shape(
        type="circle",
        xref="x",
        yref="y",
        x0=-22,
        y0=-22,
        x1=22,
        y1=22,
        line_color="LightSeaGreen",
        fillcolor="#7f7f7f",
        opacity=0.3,
    )

    return html.Div(
        [
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(pop_table(player_id, cnx)),
                        ]
                    ),
                    publish_avg_7_day_change(player_id, cnx),
                    dbc.Col(dcc.Graph(figure=fig, config={"displaylogo": False})),
                    dcc.Graph(figure=map, config={"displaylogo": False}),
                ]
            ),
        ],
    )


def publish_avg_7_day_change(player_id, cnx):
    query = f"""SELECT inserted_at, player_id, SUM(population) AS total_population, COUNT(village_id) AS village_count
                FROM map_history
                WHERE player_id = {player_id}
                GROUP BY inserted_at, player_id;"""
    df = pd.read_sql_query(query, cnx)

    df = df.sort_values(by="inserted_at")
    df["population_change"] = df["total_population"].diff(periods=7)
    average_change = df["population_change"].mean()

    df["inserted_at"] = pd.to_datetime(df["inserted_at"], unit="s")
    df["new_village_settled"] = df["village_count"].diff() > 0
    df["time_to_settle"] = df[df["new_village_settled"]]["inserted_at"].diff()
    df["time_to_settle_days"] = df["time_to_settle"].dt.total_seconds() / (60 * 60 * 24)
    average_days_to_settle = df["time_to_settle_days"].mean()

    print(average_change)
    print(average_days_to_settle)

    average_change_label = html.Label(
        f"Average 7 Day Change: {average_change:,.2f}",
        style={"font-weight": "bold", "font-size": "large"},
    )
    average_days_to_settle_label = html.Label(
        f"Average Days to Settle: {average_days_to_settle:,.2f}",
        style={"font-weight": "bold", "font-size": "large"},
    )

    return dbc.Row(
        [
            dbc.Col(average_change_label),
            dbc.Col(average_days_to_settle_label),
        ]
    )


def add_pop_diff_markdown(df):
    df["today"] = df["today"].astype(str)
    df["yesterday"] = df["yesterday"].astype(str)
    df["two_days_ago"] = df["two_days_ago"].astype(str)
    df["three_days_ago"] = df["three_days_ago"].astype(str)
    df["four_days_ago"] = df["four_days_ago"].astype(str)
    df["five_days_ago"] = df["five_days_ago"].astype(str)

    for index, row in df.iterrows():
        today_markdown = generate_markdown(row["today"], row["yesterday"])
        yesterday_markdown = generate_markdown(row["yesterday"], row["two_days_ago"])
        two_days_ago_markdown = generate_markdown(
            row["two_days_ago"], row["three_days_ago"]
        )
        three_days_ago_markdown = generate_markdown(
            row["three_days_ago"], row["four_days_ago"]
        )
        four_days_ago_markdown = generate_markdown(
            row["four_days_ago"], row["five_days_ago"]
        )
        five_days_ago_markdown = generate_markdown(
            row["five_days_ago"], row["six_days_ago"]
        )

        df.at[index, "today"] = str(df.at[index, "today"]) + " " + today_markdown
        df.at[index, "yesterday"] = (
            str(df.at[index, "yesterday"]) + " " + yesterday_markdown
        )
        df.at[index, "two_days_ago"] = (
            str(df.at[index, "two_days_ago"]) + " " + two_days_ago_markdown
        )
        df.at[index, "three_days_ago"] = (
            str(df.at[index, "three_days_ago"]) + " " + three_days_ago_markdown
        )
        df.at[index, "four_days_ago"] = (
            str(df.at[index, "four_days_ago"]) + " " + four_days_ago_markdown
        )
        df.at[index, "five_days_ago"] = (
            str(df.at[index, "five_days_ago"]) + " " + five_days_ago_markdown
        )


def generate_markdown(first, second):
    first = int(first)
    second = int(second)

    if first == 0:
        return ""

    pop_diff = first - second
    markdown = ""
    if pop_diff > 0:
        markdown = f'<font color="green">(+{pop_diff})</font>'
    elif pop_diff < 0:
        markdown = f'<font color="red">({pop_diff})</font>'
    else:
        markdown = f"({pop_diff})"
    return markdown


def add_total_row(df):
    total_row = {
        "village_name": "Total",
        "founded": "",
        "today": df["today"].sum(),
        "yesterday": df["yesterday"].sum(),
        "two_days_ago": df["two_days_ago"].sum(),
        "three_days_ago": df["three_days_ago"].sum(),
        "four_days_ago": df["four_days_ago"].sum(),
        "five_days_ago": df["five_days_ago"].sum(),
        "six_days_ago": df["six_days_ago"].sum(),
    }
    df = df.append(total_row, ignore_index=True)
    return df
