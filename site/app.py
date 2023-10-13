import sqlite3

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, dcc, html

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.LUX],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Travstat"

server = app.server

cnx = sqlite3.connect("../databases/game_servers/am3.db")
updated_at = pd.read_sql_query(
    "select max(strftime('%Y-%m-%d', datetime(inserted_at, 'unixepoch', 'localtime'))) as updated_at from map_history;",
    cnx,
)

from dash import html
import dash_bootstrap_components as dbc


def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(page["name"], href=page["relative_path"]))
            for page in dash.page_registry.values()
            if "detail" not in page["name"]
        ],
        brand="Travstat",
        brand_href="/",
        color="primary",
        dark=True,
    )

    return navbar


app.layout = html.Div(
    [
        create_navbar(),
        html.Br(),
        dbc.Container(
            children=[
                html.Div(
                    [
                        dash.page_container,
                    ]
                ),
                html.Hr(),
                html.Footer(
                    children=[
                        html.P(f"Last updated: {updated_at['updated_at'].iat[0]}"),
                    ]
                ),
            ]
        ),
    ]
)


if __name__ == "__main__":
    app.run_server()
