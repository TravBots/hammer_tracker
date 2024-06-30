import sqlite3

import dash
import pandas as pd
from dash import Input, Output, callback, dash_table, html

dash.register_page(__name__)

cnx = sqlite3.connect("../databases/game_servers/am2.db")


def data_table(cnx: sqlite3.Connection):
    df = pd.read_sql_query(
        """select 
            '['||player_name||']('||'players/'||player_id||')' as player_name, 
            alliance_tag, 
            sum(population) as population, 
            count(*) as village_count, 
            sum(population)/count(*) as avg_village_size, 
            row_number() over(order by sum(population) desc) as rank 
        from x_world 
        where player_name <> 'Natars'
        group by 1, 2""",
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
                "name": "Player Name",
                "id": "player_name",
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
                "name": "Alliance",
                "id": "alliance_tag",
                "type": "text",
                "presentation": "markdown",
            },
            {
                "name": "Village Count",
                "id": "village_count",
                "type": "numeric",
                "presentation": "markdown",
            },
            {
                "name": "Average Village Size",
                "id": "avg_village_size",
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
        style_table={"width": "90%"},
        style_data={
            "width": "150px",
            "minWidth": "150px",
            "maxWidth": "150px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        markdown_options={"link_target": "_self", "html": True},
    )

    return fig


layout = html.Div([html.Div(id="players-table", children=data_table(cnx))])


@callback(Output("players-table", "children"), Input("stored-server", "data"))
def update_table(data):
    cnx = sqlite3.connect(f"../databases/game_servers/{data['server_code']}.db")
    return data_table(cnx)
