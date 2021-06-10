# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import base64
import datetime
import io
from optimize_cpp_cmaes import Optimizer
import plotly.express as px

colorseq = px.colors.qualitative.Plotly

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

traj_data = pd.DataFrame()
traj_filepath = ""
n_samples = 0

optimizer = Optimizer()

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
            'width': '800px',
            'margin': '10px'
        }
    ),

    html.Button(
        'Optimize',
        id='optimize-button',
        n_clicks=0,
        style={
            'padding': '10',
            'margin': '10px'
        }
    ),

    dcc.Graph(
        id='3Dtraj',
        figure=go.Figure(),
        style={
            'width': '600px',
        }
    ),
    
    dcc.Graph(
        id='2Dtraj',
        figure=make_subplots(rows=9, cols=1),
        style={
            # 'width': '800px',
            # 'height': '1200px',
        }
    ),

    # html.Div(
    #     id='output-coeffs',
    #     style={
    #         'width': '100px',
    #         'margin': '10px'
    #     }
    # ),
], style={'columnCount': 2})


@app.callback(
    dash.dependencies.Output('output-data-upload', 'children'),
    # dash.dependencies.Output('output-coeffs', 'children'),],
    [dash.dependencies.Input('upload-data', 'contents')],
    [dash.dependencies.State('upload-data', 'filename')])
def load_data(contents, filename):
    if contents is not None:
        global traj_data, traj_filepath, n_samples
        traj_filepath = "/home/fidel/repos/deepaero/" + filename
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
            traj_data = df # Store dataset in global variable traj_data
            n_samples = df.shape[0] # Store number of samples
            optimizer.loadTrajectory(traj_filepath, n_samples)
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        df2 = pd.DataFrame({'p': [2, 3], 'q': [3, 4]})

        table1 = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=df.head(3).round(decimals=2).to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                style_as_list_view=True,
                style_cell={'padding': '5px'},
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
            ),
        ])

        table2 = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                id='coeffs',
                data=df2.head(3).round(decimals=2).to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df2.columns],
                style_as_list_view=True,
                style_cell={'padding': '5px'},
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
            ),
        ])

        us = 0
        N = 100
        for _ in range(N):
            us += optimizer.getEvaluationTimeInMicroseconds()
        print(f'Microseconds: {us/N}')
        print(f'Number of samples: {n_samples}')
        print(f'Number of states: {df.shape[1]}')
        return table1#, table2

@app.callback(
    [dash.dependencies.Output('3Dtraj', 'figure'),
    dash.dependencies.Output('2Dtraj', 'figure'),],
    [dash.dependencies.Input('optimize-button', 'n_clicks'),
    dash.dependencies.Input('output-data-upload', 'children')],
    [dash.dependencies.State('3Dtraj', 'figure'),
    dash.dependencies.State('2Dtraj', 'figure')])
def run_optimization(n_clicks, contents, current_fig_3D, current_fig_2D):
    global traj_data
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'optimize-button' in changed_id:
        df_optim, df_real = optimizer.optimize()
        fig_3D = go.Figure()
        fig_3D.add_trace(
            go.Scatter3d(
                x=df_real['posNorth'],
                y=df_real['posEast'],
                z=-df_real['posDown'],
                mode='lines',
                line={"color": 'red'},
                legendgroup=1,
                hovertext="Real",
                showlegend=True,
                name="Real"
            )
        )
        fig_3D.add_trace(
            go.Scatter3d(
                x=df_optim['posNorth'],
                y=df_optim['posEast'],
                z=-df_optim['posDown'],
                mode='lines',
                line={"color": 'blue'},
                legendgroup=1,
                hovertext="Optim",
                showlegend=True,
                name="Optimized"
            )
        )
        fig_3D.update_layout(
            margin=dict(l=25, r=25, t=25, b=25),
            paper_bgcolor="White",
            title_text="3D trajectory",
        )
        fig_2D = make_subplots(rows=9, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.02)
        fig_2D.add_trace(go.Scatter(name='roll_real', y=df_real['roll'], line=dict(shape='linear', color=colorseq[0], dash='solid'), opacity=1), row=1, col=1)
        fig_2D.add_trace(go.Scatter(name='roll_optim', y=df_optim['roll'], line=dict(shape='linear', color=colorseq[0], dash='solid'), opacity=0.5), row=1, col=1)
        fig_2D.add_trace(go.Scatter(name='pitch_real', y=df_real['pitch'], line=dict(shape='linear', color=colorseq[1], dash='solid'), opacity=1), row=2, col=1)
        fig_2D.add_trace(go.Scatter(name='pitch_optim', y=df_optim['pitch'], line=dict(shape='linear', color=colorseq[1], dash='solid'), opacity=0.5), row=2, col=1)
        fig_2D.add_trace(go.Scatter(name='yaw_real', y=df_real['yaw'], line=dict(shape='linear', color=colorseq[2], dash='solid'), opacity=1), row=3, col=1)
        fig_2D.add_trace(go.Scatter(name='yaw_optim', y=df_optim['yaw'], line=dict(shape='linear', color=colorseq[2], dash='solid'), opacity=0.5), row=3, col=1)
        fig_2D.add_trace(go.Scatter(name='vx_real', y=df_real['vx'], line=dict(shape='linear', color=colorseq[3], dash='solid'), opacity=1), row=4, col=1)
        fig_2D.add_trace(go.Scatter(name='vx_optim', y=df_optim['vx'], line=dict(shape='linear', color=colorseq[3], dash='solid'), opacity=0.5), row=4, col=1)
        fig_2D.add_trace(go.Scatter(name='vy_real', y=df_real['vy'], line=dict(shape='linear', color=colorseq[4], dash='solid'), opacity=1), row=5, col=1)
        fig_2D.add_trace(go.Scatter(name='vy_optim', y=df_optim['vy'], line=dict(shape='linear', color=colorseq[4], dash='solid'), opacity=0.5), row=5, col=1)
        fig_2D.add_trace(go.Scatter(name='vz_real', y=df_real['vz'], line=dict(shape='linear', color=colorseq[5], dash='solid'), opacity=1), row=6, col=1)
        fig_2D.add_trace(go.Scatter(name='vz_optim', y=df_optim['vz'], line=dict(shape='linear', color=colorseq[5], dash='solid'), opacity=0.5), row=6, col=1)
        fig_2D.add_trace(go.Scatter(name='p_real', y=df_real['p'], line=dict(shape='linear', color=colorseq[6], dash='solid'), opacity=1), row=7, col=1)
        fig_2D.add_trace(go.Scatter(name='p_optim', y=df_optim['p'], line=dict(shape='linear', color=colorseq[6], dash='solid'), opacity=0.5), row=7, col=1)
        fig_2D.add_trace(go.Scatter(name='q_real', y=df_real['q'], line=dict(shape='linear', color=colorseq[7], dash='solid'), opacity=1), row=8, col=1)
        fig_2D.add_trace(go.Scatter(name='q_optim', y=df_optim['q'], line=dict(shape='linear', color=colorseq[7], dash='solid'), opacity=0.5), row=8, col=1)
        fig_2D.add_trace(go.Scatter(name='r_real', y=df_real['r'], line=dict(shape='linear', color=colorseq[8], dash='solid'), opacity=1), row=9, col=1)
        fig_2D.add_trace(go.Scatter(name='r_optim', y=df_optim['r'], line=dict(shape='linear', color=colorseq[8], dash='solid'), opacity=0.5), row=9, col=1)
        fig_2D.update_layout(height=800, width=800, title_text="2D trajectories")
    elif 'output-data-upload' in changed_id and not traj_data.empty:
        fig_3D = go.Figure()
        fig_3D.add_trace(
            go.Scatter3d(
                x=traj_data['posNorth'],
                y=traj_data['posEast'],
                z=-traj_data['posDown'],
                mode='lines',
                line={"color": 'red'},
                legendgroup=1,
                hovertext="Real",
                showlegend=True,
                name="Real"
            )
        )
        fig_3D.update_layout(
            margin=dict(l=25, r=25, t=25, b=25),
            paper_bgcolor="White",
            title_text="3D trajectory",
        )
        fig_2D = make_subplots(rows=9, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.02)
        fig_2D.add_trace(go.Scatter(name='roll', y=traj_data['roll']), row=1, col=1)
        fig_2D.add_trace(go.Scatter(name='pitch', y=traj_data['pitch']), row=2, col=1)
        fig_2D.add_trace(go.Scatter(name='yaw', y=traj_data['yaw']), row=3, col=1)
        fig_2D.add_trace(go.Scatter(name='vx', y=traj_data['vx']), row=4, col=1)
        fig_2D.add_trace(go.Scatter(name='vy', y=traj_data['vy']), row=5, col=1)
        fig_2D.add_trace(go.Scatter(name='vz', y=traj_data['vz']), row=6, col=1)
        fig_2D.add_trace(go.Scatter(name='p', y=traj_data['p']), row=7, col=1)
        fig_2D.add_trace(go.Scatter(name='q', y=traj_data['q']), row=8, col=1)
        fig_2D.add_trace(go.Scatter(name='r', y=traj_data['r']), row=9, col=1)
        fig_2D.update_layout(height=800, width=800, title_text="2D trajectories")
    else:
        fig_3D = current_fig_3D
        fig_2D = current_fig_2D
    return fig_3D, fig_2D

if __name__ == '__main__':
    app.run_server(debug=True)
