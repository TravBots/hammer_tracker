import sqlite3

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, dcc, html

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.LUX],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Travstat"

server = app.server


def get_last_updated(server):
    cnx = sqlite3.connect(f"../databases/game_servers/{server}.db")
    updated_at = pd.read_sql_query(
        "select max(strftime('%Y-%m-%d', datetime(inserted_at, 'unixepoch', 'localtime'))) as updated_at from map_history;",
        cnx,
    )
    return updated_at["updated_at"].iat[0]



def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink(page["name"], id=page["name"], href=page["relative_path"])
            )
            for page in dash.page_registry.values()
            if "detail" not in page["name"]
        ]
        + [
            dcc.Dropdown(
                id="server-dropdown",
                options=[
                    {"label": "America 2", "value": "am2"},
                    {"label": "America 3", "value": "am3"},
                ],
                clearable=False,
                style={"width": "150px", "padding-right": "10px"},
                value="am2",  # Optionally set a default value
            )
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
                    id="footer",
                    children=[
                        html.P(f"Last updated: {get_last_updated('am2')}"),
                    ],
                ),
            ]
        ),
        dcc.Store(id="stored-server"),
    ]
)


@app.callback(Output("stored-server", "data"), Input("server-dropdown", "value"))
def update_store(value):
    updated_at = get_last_updated(value)
    return {"server_code": value, "updated_at": updated_at}


@app.callback(Output("footer", "children"), Input("stored-server", "data"))
def display_value(data):
    return [
        html.P(f"Server: {data['server_code']}; Last updated: {data['updated_at']}")
    ]


if __name__ == "__main__":
    app.run_server()
