import dash
from dash import html

dash.register_page(__name__, path_template="/alliance/<alliance_id>")


def layout(alliance_id=None):
    return html.Div(f"The user requested report ID: {alliance_id}.")
