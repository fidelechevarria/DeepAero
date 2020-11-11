# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import base64
import datetime
import io
import optimize_cpp_cmaes

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H3(children='DeepAero'),

    html.Div(children='''
        Parameter identification for dynamic systems.
    '''),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),
        style={
            'width': '500px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple = False # Do not allow multiple files to be uploaded
    ),

    html.Div(
        id='output-data-upload',
        style={
            'width': '800px'
        }
    ),

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

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            data=df.head().round(decimals=2).to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_as_list_view=True,
            style_cell={'padding': '5px'},
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },
        ),
    ])

@app.callback(
    dash.dependencies.Output('output-data-upload', 'children'),
    [dash.dependencies.Input('upload-data', 'contents')],
    [dash.dependencies.State('upload-data', 'filename')])
def load_data(contents, name):
    if contents is not None:
        return parse_contents(contents, name)

@app.callback(
    dash.dependencies.Output('3Dtraj', 'figure'),
    [dash.dependencies.Input('optimize-button', 'n_clicks')],
    [dash.dependencies.State('3Dtraj', 'figure')])
def run_optimization(n_clicks, current_fig):
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