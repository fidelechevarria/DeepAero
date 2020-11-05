# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import optimize_cpp

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_optim, df_real = optimize_cpp.optimize()

fig = go.Figure()
fig.add_trace(
    go.Scatter3d(
        x=df_optim['north'],
        y=df_optim['east'],
        z=-df_optim['down'],
        mode='lines',
        line={"color": 'blue'},
        legendgroup=1,
        hovertext="Optim",
        showlegend=True,
        name="Optimized"
    )
)
fig.add_trace(
    go.Scatter3d(
        x=df_real['north'],
        y=df_real['east'],
        z=-df_real['down'],
        mode='lines',
        line={"color": 'red'},
        legendgroup=1,
        hovertext="Real",
        showlegend=True,
        name="Real"
    )
)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)