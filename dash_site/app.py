import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html, dash_table
import dash
import datetime
import sqlite3

import dash_bootstrap_components as dbc

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=external_stylesheets,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Travstat"

server = app.server

cnx = sqlite3.connect("../core/databases/map.db")
updated_at = pd.read_sql_query(
    "select max(strftime('%Y-%m-%d', datetime(inserted_at, 'unixepoch', 'localtime'))) as updated_at from map_history;",
    cnx,
)

app.layout = html.Div(
    dbc.Container(
        children=[
            html.Div(
                [
                    html.H1("Welcome to Travstat"),
                    html.Div(
                        [
                            html.Div(
                                dcc.Link(
                                    f"{page['name']}",
                                    href=page["relative_path"],
                                )
                            )
                            for page in dash.page_registry.values()
                            if "detail" not in page["name"]
                        ]
                    ),
                    dash.page_container,
                ]
            ),
            html.Footer(
                children=[
                    html.P(f"Last updated: {updated_at['updated_at'].iat[0]}"),
                ]
            ),
        ]
    )
)


if __name__ == "__main__":
    app.run_server()
