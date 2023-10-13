import sqlite3

import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html

dash.register_page(__name__)

cnx = sqlite3.connect("../databases/game_servers/am3.db")
query = f"""
select alliance_tag, sum(population) as total_pop from x_world 
where alliance_tag <> ''
group by alliance_tag 
order by total_pop desc limit 20
;"""
alliances = data = pd.read_sql_query(query, cnx)
layout = html.Div(
    [
        html.H4("Select the alliances you would like to see below"),
        dcc.Dropdown(
            id="dropdown",
            options=alliances["alliance_tag"],
            value=[alliances["alliance_tag"].iat[i] for i in range(4)],
            multi=True,
        ),
        dcc.Graph(
            id="graph",
            config={"displaylogo": False},
        ),
    ],
)


@callback(Output("graph", "figure"), Input("dropdown", "value"))
def map(alliances):
    alliances = ", ".join(f"'{alliance}'" for alliance in alliances)
    cnx = sqlite3.connect("../databases/game_servers/am3.db")
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
    FROM x_world where alliance_tag in ({alliances});"""
    print(query)

    data = pd.read_sql_query(query, cnx)
    fig = px.scatter(
        data_frame=data,
        x="X Coordinate",
        y="Y Coordinate",
        color="Alliance Name",
        symbol="Alliance Name",
        hover_data=["Player Name", "Village Name", "Tribe", "Population", "Capital?"],
        width=1100,
        height=1000,
    )

    fig.update_xaxes(range=[-200, 200])
    fig.update_yaxes(range=[-200, 200])
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    fig.update_traces(marker={"size": 7})

    fig.add_shape(
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
    return fig
