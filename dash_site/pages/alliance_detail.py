import dash
from dash import html, dcc
import sqlite3
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path_template="/alliance/<alliance_id>")


def layout(alliance_id=None):
    cnx = sqlite3.connect("../core/databases/map.db")
    # TODO: Pass alliance_id as a param instead of f-string. This is insecure.
    query = f"select strftime('%Y-%m-%d', datetime(inserted_at, 'unixepoch', 'localtime')) as date, alliance_id, sum(population) as population from map_history where alliance_id = {alliance_id} group by 1,2 order by 1;"
    history = pd.read_sql_query(query, cnx)
    query = f"select alliance_tag, sum(population) as population from x_world where alliance_id = {alliance_id} group by 1"
    alliance = pd.read_sql_query(query, cnx)

    ref = min(len(history) - 1, 7)
    fig = go.Figure(
        go.Indicator(
            mode="number+delta",
            value=history["population"][ref],
            delta={
                "reference": alliance["population"][0],
                "valueformat": ".0f",
            },
            title={"text": alliance["alliance_tag"][0]},
            domain={"y": [0, 1], "x": [0.25, 0.75]},
        )
    )
    fig.add_trace(go.Scatter(y=history["population"]))

    fig.update_layout(xaxis={"range": [0, len(history) - 1]})

    return html.Div(dcc.Graph(figure=fig, config={"displaylogo": False}))
