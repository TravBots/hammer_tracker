import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

import sqlite3

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

cnx = sqlite3.connect("../core/databases/map.db")
query = f"""
select alliance_tag, sum(population) as total_pop from x_world 
where alliance_tag <> ''
group by alliance_tag 
order by total_pop desc limit 20
;"""
alliances = data = pd.read_sql_query(query, cnx)
app.layout = html.Div(
    children=[
        html.H4("Select the alliances you would like to see below"),
        dcc.Dropdown(
            id="dropdown",
            options=alliances["alliance_tag"],
            value=[alliances["alliance_tag"].iat[i] for i in range(4)],
            multi=True,
        ),
        dcc.Graph(id="graph"),
    ]
)


@app.callback(Output("graph", "figure"), Input("dropdown", "value"))
def map(alliances):
    alliances = ", ".join(f"'{alliance}'" for alliance in alliances)
    cnx = sqlite3.connect("../core/databases/map.db")
    query = f"SELECT * FROM x_world where alliance_tag in ({alliances});"
    print(query)

    data = pd.read_sql_query(query, cnx)
    fig = px.scatter(
        data_frame=data,
        x="x_coordinate",
        y="y_coordinate",
        color="alliance_tag",
        symbol="alliance_tag",
        hover_data=["village_name", "population", "capital"],
        width=1100,
        height=1000,
    )

    fig.update_xaxes(range=[-200, 200])
    fig.update_yaxes(range=[-200, 200])
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    return fig


if __name__ == "__main__":
    app.run_server()
