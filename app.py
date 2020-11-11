# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import optimize_cpp_cmaes

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H3(children='DeepAero'),

    html.Div(children='''
        Parameter identification for dynamic systems.
    '''),

    html.Button(
        'Optimize',
        id='optimize-button',
        n_clicks=0
    ),

    dcc.Graph(
        id='3Dtraj',
        figure=go.Figure(),
        style={
            'width': '600px'
        }
    )
])

@app.callback(
    dash.dependencies.Output('3Dtraj', 'figure'),
    [dash.dependencies.Input('optimize-button', 'n_clicks')],
    [dash.dependencies.State('3Dtraj', 'figure')])
def update_output(n_clicks, current_fig):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'optimize-button' in changed_id:
        df_optim, df_real = optimize_cpp_cmaes.optimize()
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
        fig.update_layout(
            margin=dict(l=25, r=25, t=25, b=25),
            paper_bgcolor="White",
        )
    else:
        fig = current_fig
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)