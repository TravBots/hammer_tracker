import dash
from dash import html, dcc, callback, Input, Output

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html, dash_table
import dash
import sqlite3

dash.register_page(__name__)

cnx = sqlite3.connect("../core/databases/map.db")


def data_table(cnx: sqlite3.Connection):
    df = pd.read_sql_query(
        "select player_name, alliance_tag, sum(population) as population, count(*) as village_count, sum(population)/count(*) as avg_village_size, row_number() over(order by sum(population) desc) as rank from x_world where player_name <> 'Natars'group by 1, 2",
        cnx,
    )
    fig = dash_table.DataTable(
        columns=[
            {"name": "Rank", "id": "rank", "type": "numeric"},
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


layout = html.Div(
    [
        html.Div(
            [
                data_table(cnx),
            ]
        ),
        html.Br(),
        html.Div(id="analytics-output"),
    ]
)
