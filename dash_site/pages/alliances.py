import sqlite3

import dash
import pandas as pd
from dash import dash_table, html

dash.register_page(__name__)

cnx = sqlite3.connect("../core/databases/map.db")


def data_table(cnx: sqlite3.Connection):
    df = pd.read_sql_query(
        f"""select 
            '['||alliance_tag||']('||'alliances/'||alliance_id||')' as alliance_tag, 
            sum(population) as population, 
            count(distinct player_id) as player_count, 
            sum(population)/count(distinct player_id) as avg_player_size, 
            row_number() over(order by sum(population) desc) as rank 
        from x_world 
        where alliance_tag <> '' 
        group by 1""",
        cnx,
    )
    fig = dash_table.DataTable(
        columns=[
            {
                "name": "Rank",
                "id": "rank",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": "Alliance Name",
                "id": "alliance_tag",
                "type": "text",
                "presentation": "markdown",
            },
            {
                "name": "Population",
                "id": "population",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": "Player Count",
                "id": "player_count",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": "Average Player Size",
                "id": "avg_player_size",
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
