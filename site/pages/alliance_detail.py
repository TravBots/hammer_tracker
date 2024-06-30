import sqlite3

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output
import dash_daq as daq


dash.register_page(__name__, path_template="/alliances/<alliance_id>")


def layout(server_id="am2", alliance_id="1"):
    return html.Div(id="alliance-detail", children=get_children(server_id, alliance_id))


def get_children(server_id, alliance_id):
    return [
        html.H2(f"Alliance ID: {alliance_id}"),
        dcc.Graph(
            id="alliance-pop-chart",
            figure=create_pop_chart(server_id, alliance_id),
            config={"displaylogo": False},
        ),
        daq.ToggleSwitch(
            id="capital-toggle",
            value=False,
        ),
        dcc.Graph(id="alliance-villages", config={"displaylogo": False}),
        dcc.Store(id="alliance-id", data=alliance_id),
    ]


@callback(
    Output("alliance-villages", "figure"),
    Input("alliance-id", "data"),
    Input("stored-server", "data"),
    Input("capital-toggle", "value"),
)
def create_map(alliance_id, data, filter_capitals):
    cnx = sqlite3.connect(f"../databases/game_servers/{data['server_code']}.db")
    print(f"Creating map for alliance {alliance_id}")
    print(f"Filter capitals: {filter_capitals}")
    capital_filter = "and capital" if filter_capitals else ""
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
    FROM x_world where alliance_id = {alliance_id}
    {capital_filter}
    order by player_name;"""

    data = pd.read_sql_query(query, cnx)
    map = px.scatter(
        data_frame=data,
        x="X Coordinate",
        y="Y Coordinate",
        color="Player Name",
        hover_data=["Player Name", "Village Name", "Tribe", "Population", "Capital?"],
        width=1100,
        height=1000,
    )

    map.update_xaxes(range=[-200, 200])
    map.update_yaxes(range=[-200, 200])
    map.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    map.update_traces(marker={"size": 7})

    map.add_shape(
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

    return map


def create_pop_chart(server_id, alliance_id):
    cnx = sqlite3.connect(f"../databases/game_servers/{server_id}.db")
    # TODO: Pass alliance_id as a param instead of f-string. This is insecure.
    query = f"""
        select 
            v_map_history.date, 
            alliance_id, 
            sum(population) as population 
        from v_map_history 
        join v_server_numbers
            on v_server_numbers.date = v_map_history.date
        where v_map_history.alliance_id = {alliance_id} 
        and v_server_numbers.server_number = (select max(server_number) from v_server_numbers)
        group by 1,2 
        order by 1;
        """
    history = pd.read_sql_query(query, cnx)
    query = f"select alliance_tag, sum(population) as population from x_world where alliance_id = {alliance_id} group by 1"
    alliance = pd.read_sql_query(query, cnx)

    if history.empty or alliance.empty:
        return go.Figure()

    ref = max(0, len(history) - 8)
    fig = go.Figure(
        go.Indicator(
            mode="number+delta",
            value=history["population"][len(history) - 1],
            delta={
                "reference": history["population"][ref],
                "valueformat": ".0f",
            },
            title={"text": f"{alliance['alliance_tag'][0]} (7 day diff)"},
            domain={"y": [0, 1], "x": [0.25, 0.75]},
        )
    )
    fig.add_trace(
        go.Scatter(y=history["population"], x=history["date"], name="Population")
    )

    return fig


@callback(
    Output("alliance-pop-chart", "figure"),
    Input("stored-server", "data"),
    Input("alliance-detail", "children"),
)
def update(data, current_children):
    alliance_id = 1

    if current_children is not None:
        alliance_str = current_children[0]["props"]["children"]
        alliance_id = alliance_str.split(": ")[1]

    print('data["server_code"]:', data["server_code"])

    return create_pop_chart(data["server_code"], alliance_id)
