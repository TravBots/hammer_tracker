import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html, dash_table

import datetime
import sqlite3

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Travstat | America 3"

server = app.server

cnx = sqlite3.connect("../core/databases/map.db")
query = f"""
select alliance_tag, sum(population) as total_pop from x_world 
where alliance_tag <> ''
group by alliance_tag 
order by total_pop desc limit 20
;"""
alliances = data = pd.read_sql_query(query, cnx)
updated_at = pd.read_sql_query(
    "select max(strftime('%Y-%m-%d', datetime(inserted_at, 'unixepoch', 'localtime'))) as updated_at from map_history;",
    cnx,
)


def data_table(cnx: sqlite3.Connection):
    df = pd.read_sql_query(
        "select player_name, alliance_tag, sum(population) as population, count(*) as village_count, sum(population)/count(*) as avg_village_size from x_world group by 1, 2",
        cnx,
    )
    fig = dash_table.DataTable(
        columns=[
            {"name": "Player Name", "id": "player_name", "type": "text"},
            {"name": "Population", "id": "population", "type": "numeric"},
            {"name": "Alliance", "id": "alliance_tag", "type": "text"},
            {"name": "Village Count", "id": "village_count", "type": "numeric"},
            {
                "name": "Average Village Size",
                "id": "avg_village_size",
                "type": "numeric",
            },
        ],
        data=df.to_dict("records"),
        filter_action="native",
        sort_action="native",
        page_action="native",
        page_current=0,
        page_size=25,
        style_table={
            "height": 800,
        },
        style_data={
            "width": "150px",
            "minWidth": "150px",
            "maxWidth": "150px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
    )

    return fig


app.layout = html.Div(
    children=[
        html.Div(
            [
                html.H4("Select the alliances you would like to see below"),
                html.P(f"Last updated: {updated_at['updated_at'].iat[0]}"),
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
        ),
        html.Div(
            [
                data_table(cnx),
            ]
        ),
    ]
)


@app.callback(Output("graph", "figure"), Input("dropdown", "value"))
def map(alliances):
    alliances = ", ".join(f"'{alliance}'" for alliance in alliances)
    cnx = sqlite3.connect("../core/databases/map.db")
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


if __name__ == "__main__":
    app.run_server()
