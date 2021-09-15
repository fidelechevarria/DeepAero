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
import numpy as np

# colorseq = px.colors.qualitative.Plotly

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
        global traj_data, traj_filepath, n_samples, time
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
            traj_data = traj_data.apply(lambda x: np.rad2deg(x) if (x.name == 'roll' or x.name == 'pitch' or x.name == 'yaw' or x.name == 'p' or x.name == 'q' or x.name == 'r') else x)
            n_samples = df.shape[0] # Store number of samples
            time = np.linspace(0, n_samples * (1 / 60), n_samples)
            print(df)
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
        df_optim, df_real = optimizer.optimize(mode='single')
        df_optim = df_optim.apply(lambda x: np.rad2deg(x) if (x.name == 'roll' or x.name == 'pitch' or x.name == 'yaw' or x.name == 'p' or x.name == 'q' or x.name == 'r') else x)
        df_real = df_real.apply(lambda x: np.rad2deg(x) if (x.name == 'roll' or x.name == 'pitch' or x.name == 'yaw' or x.name == 'p' or x.name == 'q' or x.name == 'r') else x)
        fig_3D = go.Figure()
        fig_3D.add_trace(
            go.Scatter3d(
                x=df_real['posNorth'],
                y=df_real['posEast'],
                z=-df_real['posDown'],
                mode='lines',
                line={"color": 'black'},
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
                line={"color": 'black', "dash": 'dash'},
                legendgroup=1,
                hovertext="Optim",
                showlegend=True,
                opacity=0.5,
                name="Solution"
            )
        )
        fig_3D.add_trace(
            go.Scatter3d(
                name="",
                visible=True,
                showlegend=False,
                opacity=0,
                hoverinfo='none',
                x=[traj_data['posNorth'][0],traj_data['posNorth'][0]],
                y=[traj_data['posEast'][0],traj_data['posEast'][0]],
                z=[800,980]
            )
        )
        fig_3D.update_layout(
            margin=dict(l=25, r=25, t=25, b=25),
            xaxis=dict(
                title="North (m)"
            ),
            scene=dict(
                aspectmode="data",
                xaxis=dict(
                    title="North (m)"
                ),
                yaxis=dict(
                    title="East (m)"
                ),
                zaxis=dict(
                    title="Altitude (m)"
                ),
                camera=dict(
                    projection=dict(
                        type="orthographic"
                    )
                ),
                ),
            paper_bgcolor="White",
            title_text="3D trajectory",
        )
        fig_3D.write_image('images/solution-pos.svg')
        fig_2D = make_subplots(rows=13, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.02)
        fig_2D.add_trace(go.Scatter(name='da', showlegend=False, x=time, y=traj_data['da']*200, line=dict(shape='linear', color="black", dash='solid')), row=1, col=1)
        fig_2D.add_trace(go.Scatter(name='de', showlegend=False, x=time, y=traj_data['de']*200, line=dict(shape='linear', color="black", dash='solid')), row=2, col=1)
        fig_2D.add_trace(go.Scatter(name='dr', showlegend=False, x=time, y=traj_data['dr']*200, line=dict(shape='linear', color="black", dash='solid')), row=3, col=1)
        fig_2D.add_trace(go.Scatter(name='dt', showlegend=False, x=time, y=traj_data['dt']*100, line=dict(shape='linear', color="black", dash='solid')), row=4, col=1)
        fig_2D.add_trace(go.Scatter(name='Real', showlegend=True, x=time, y=df_real['roll'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=5, col=1)
        fig_2D.add_trace(go.Scatter(name='Solution', showlegend=True, x=time, y=df_optim['roll'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=5, col=1)
        fig_2D.add_trace(go.Scatter(name='pitch_real', showlegend=False, x=time, y=df_real['pitch'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=6, col=1)
        fig_2D.add_trace(go.Scatter(name='pitch_optim', showlegend=False, x=time, y=df_optim['pitch'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=6, col=1)
        fig_2D.add_trace(go.Scatter(name='yaw_real', showlegend=False, x=time, y=df_real['yaw'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=7, col=1)
        fig_2D.add_trace(go.Scatter(name='yaw_optim', showlegend=False, x=time, y=df_optim['yaw'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=7, col=1)
        fig_2D.add_trace(go.Scatter(name='vx_real', showlegend=False, x=time, y=df_real['vx'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=8, col=1)
        fig_2D.add_trace(go.Scatter(name='vx_optim', showlegend=False, x=time, y=df_optim['vx'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=8, col=1)
        fig_2D.add_trace(go.Scatter(name='vy_real', showlegend=False, x=time, y=df_real['vy'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=9, col=1)
        fig_2D.add_trace(go.Scatter(name='vy_optim', showlegend=False, x=time, y=df_optim['vy'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=9, col=1)
        fig_2D.add_trace(go.Scatter(name='vz_real', showlegend=False, x=time, y=df_real['vz'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=10, col=1)
        fig_2D.add_trace(go.Scatter(name='vz_optim', showlegend=False, x=time, y=df_optim['vz'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=10, col=1)
        fig_2D.add_trace(go.Scatter(name='p_real', showlegend=False, x=time, y=df_real['p'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=11, col=1)
        fig_2D.add_trace(go.Scatter(name='p_optim', showlegend=False, x=time, y=df_optim['p'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=11, col=1)
        fig_2D.add_trace(go.Scatter(name='q_real', showlegend=False, x=time, y=df_real['q'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=12, col=1)
        fig_2D.add_trace(go.Scatter(name='q_optim', showlegend=False, x=time, y=df_optim['q'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=12, col=1)
        fig_2D.add_trace(go.Scatter(name='r_real', showlegend=False, x=time, y=df_real['r'], line=dict(shape='linear', color="black", dash='solid'), opacity=1), row=13, col=1)
        fig_2D.add_trace(go.Scatter(name='r_optim', showlegend=False, x=time, y=df_optim['r'], line=dict(shape='linear', color="black", dash='dash'), opacity=0.5), row=13, col=1)
        fig_2D.update_layout(height=1000, width=800, title_text="2D trajectories")
        fig_2D.update_yaxes(title_text="da (%)", row=1, col=1)
        fig_2D.update_yaxes(title_text="de (%)", row=2, col=1)
        fig_2D.update_yaxes(title_text="dr (%)", row=3, col=1)
        fig_2D.update_yaxes(title_text="dt (%)", row=4, col=1)
        fig_2D.update_yaxes(title_text="φ (°)", row=5, col=1)
        fig_2D.update_yaxes(title_text="θ (°)", row=6, col=1)
        fig_2D.update_yaxes(title_text="ψ (°)", row=7, col=1)
        fig_2D.update_yaxes(title_text="vx (m/s)", row=8, col=1)
        fig_2D.update_yaxes(title_text="vy (m/s)", row=9, col=1)
        fig_2D.update_yaxes(title_text="vz (m/s)", row=10, col=1)
        fig_2D.update_yaxes(title_text="p (°/s)", row=11, col=1)
        fig_2D.update_yaxes(title_text="q (°/s)", row=12, col=1)
        fig_2D.update_yaxes(title_text="r (°/s)", row=13, col=1)
        fig_2D.update_xaxes(title_text="Time (s)", row=13, col=1)
        fig_2D.write_image('images/solution-states.svg')
    elif 'output-data-upload' in changed_id and not traj_data.empty:
        fig_3D = go.Figure()
        fig_3D.add_trace(
            go.Scatter3d(
                x=traj_data['posNorth'],
                y=traj_data['posEast'],
                z=-traj_data['posDown'],
                mode='lines',
                line={"color": 'black'},
                legendgroup=1,
                hovertext="Real",
                showlegend=True,
                name="Real",
            )
        )
        fig_3D.add_trace(
            go.Scatter3d(
                name="",
                visible=True,
                showlegend=False,
                opacity=0,
                hoverinfo='none',
                x=[traj_data['posNorth'][0],traj_data['posNorth'][0]],
                y=[traj_data['posEast'][0],traj_data['posEast'][0]],
                z=[800,980]
            )
        )
        fig_3D.update_layout(
            margin=dict(l=25, r=25, t=25, b=25),
            scene=dict(
                xaxis=dict(
                    title="North (m)"
                ),
                yaxis=dict(
                    title="East (m)"
                ),
                zaxis=dict(
                    title="Altitude (m)"
                ),
                aspectmode="data",
                camera=dict(
                    projection=dict(
                        type="orthographic"
                    )
                ),
                ),
            paper_bgcolor="White",
            title_text="3D trajectory",
        )
        fig_3D.write_image('images/real-pos.svg')
        fig_2D = make_subplots(rows=13, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.02)
        fig_2D.add_trace(go.Scatter(name='da', showlegend=False, x=time, y=traj_data['da']*200, line=dict(shape='linear', color="black", dash='solid')), row=1, col=1)
        fig_2D.add_trace(go.Scatter(name='de', showlegend=False, x=time, y=traj_data['de']*200, line=dict(shape='linear', color="black", dash='solid')), row=2, col=1)
        fig_2D.add_trace(go.Scatter(name='dr', showlegend=False, x=time, y=traj_data['dr']*200, line=dict(shape='linear', color="black", dash='solid')), row=3, col=1)
        fig_2D.add_trace(go.Scatter(name='dt', showlegend=False, x=time, y=traj_data['dt']*100, line=dict(shape='linear', color="black", dash='solid')), row=4, col=1)
        fig_2D.add_trace(go.Scatter(name='Real', showlegend=True, x=time, y=traj_data['roll'], line=dict(shape='linear', color="black", dash='solid')), row=5, col=1)
        fig_2D.add_trace(go.Scatter(name='pitch', showlegend=False, x=time, y=traj_data['pitch'], line=dict(shape='linear', color="black", dash='solid')), row=6, col=1)
        fig_2D.add_trace(go.Scatter(name='yaw', showlegend=False, x=time, y=traj_data['yaw'], line=dict(shape='linear', color="black", dash='solid')), row=7, col=1)
        fig_2D.add_trace(go.Scatter(name='vx', showlegend=False, x=time, y=traj_data['vx'], line=dict(shape='linear', color="black", dash='solid')), row=8, col=1)
        fig_2D.add_trace(go.Scatter(name='vy', showlegend=False, x=time, y=traj_data['vy'], line=dict(shape='linear', color="black", dash='solid')), row=9, col=1)
        fig_2D.add_trace(go.Scatter(name='vz', showlegend=False, x=time, y=traj_data['vz'], line=dict(shape='linear', color="black", dash='solid')), row=10, col=1)
        fig_2D.add_trace(go.Scatter(name='p', showlegend=False, x=time, y=traj_data['p'], line=dict(shape='linear', color="black", dash='solid')), row=11, col=1)
        fig_2D.add_trace(go.Scatter(name='q', showlegend=False, x=time, y=traj_data['q'], line=dict(shape='linear', color="black", dash='solid')), row=12, col=1)
        fig_2D.add_trace(go.Scatter(name='r', showlegend=False, x=time, y=traj_data['r'], line=dict(shape='linear', color="black", dash='solid')), row=13, col=1)
        fig_2D.update_layout(height=1000, width=800, title_text="2D trajectories")
        fig_2D.update_yaxes(title_text="da (%)", row=1, col=1)
        fig_2D.update_yaxes(title_text="de (%)", row=2, col=1)
        fig_2D.update_yaxes(title_text="dr (%)", row=3, col=1)
        fig_2D.update_yaxes(title_text="dt (%)", row=4, col=1)
        fig_2D.update_yaxes(title_text="φ (°)", row=5, col=1)
        fig_2D.update_yaxes(title_text="θ (°)", row=6, col=1)
        fig_2D.update_yaxes(title_text="ψ (°)", row=7, col=1)
        fig_2D.update_yaxes(title_text="vx (m/s)", row=8, col=1)
        fig_2D.update_yaxes(title_text="vy (m/s)", row=9, col=1)
        fig_2D.update_yaxes(title_text="vz (m/s)", row=10, col=1)
        fig_2D.update_yaxes(title_text="p (°/s)", row=11, col=1)
        fig_2D.update_yaxes(title_text="q (°/s)", row=12, col=1)
        fig_2D.update_yaxes(title_text="r (°/s)", row=13, col=1)
        fig_2D.update_xaxes(title_text="Time (s)", row=13, col=1)
        fig_2D.write_image('images/real-states.svg')
    else:
        fig_3D = current_fig_3D
        fig_2D = current_fig_2D
    return fig_3D, fig_2D

if __name__ == '__main__':
    app.run_server(debug=True)