import sqlite3

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, dash_table

dash.register_page(__name__, path_template="/players/<player_id>")


def pop_table(player_id, cnx):
    village_pop_query = f"select * from v_three_day_pop where player_id = {player_id};"
    print(village_pop_query)

    df = pd.read_sql_query(village_pop_query, cnx)
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
                "name": "Current Population",
                "id": "current_pop",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": "One Day Diff",
                "id": "one_day_diff",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": "Two Day Diff",
                "id": "two_day_diff",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": "Three Day Diff",
                "id": "three_day_diff",
                "type": "numeric",
                "presentation": "markdown",
            },
        ],
        data=df.to_dict("records"),
        filter_action="native",
        sort_action="native",
        page_action="native",
        page_current=0,
        page_size=25,
        style_table={
            "width": "90%",
        },
        style_data={
            "width": "150px",
            "minWidth": "150px",
            "maxWidth": "150px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        markdown_options={"link_target": "_self", "html": True},
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
                    dbc.Col(dcc.Graph(figure=fig, config={"displaylogo": False})),
                    dcc.Graph(figure=map, config={"displaylogo": False}),
                ]
            ),
        ],
    )
