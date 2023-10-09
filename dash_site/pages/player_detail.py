import sqlite3

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

dash.register_page(__name__, path_template="/players/<player_id>")


def layout(player_id=None):
    cnx = sqlite3.connect("../core/databases/map.db")
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
            dcc.Graph(figure=fig, config={"displaylogo": False}),
            dcc.Graph(figure=map, config={"displaylogo": False}),
        ]
    )
