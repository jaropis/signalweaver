import dash_core_components as dcc
import dash_html_components as html
import settings
# import glob


# # this is quick and dirty - to be removed
# def data_paths(data_path):
#     list_of_files = glob.glob(data_path + "*.csv")
#     options_list = []
#     for data_file in list_of_files:
#         file_name = data_file.split("/")[-1]
#         options_list.append({'label': file_name, 'value': data_file})
#     return options_list
#     # return [{'label': '0000.csv', 'value': "/Users/jaropis/Dropbox/Praca2/Projects/Avawomen/data/0000.csv"}]
#     # return [{'label': '2017MEN_0016_breaths.csv', 'value': "2017MEN_0016_breaths.csv"}]
#
#
# file_options_list = data_paths("/Users/jaropis/Dropbox/Praca2/Projects/Avawomen/data/")
# #file_options_list = data_paths("/home/jaropis/sweaver_data/")
settings.init()
def prepare_layout(app):
    app.layout = html.Div(id='main-panel', children=[
        html.Div([
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or',
                        html.A(' Select Files')
                    ]),

                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    multiple=False
                )
            ], className='row'),

            # Controls
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Checklist(
                                options=[
                                    {'label': 'Toggle histogram and PP', 'value': 'Hide'}],
                                value=['Hide'],
                                labelStyle={'display': 'inline-block'},
                                id='second-row-toggle'),
                            dcc.Checklist(
                                options=[{'label': 'Invert ECG', 'value': 'Invert'}],
                                value=['Invert'],
                                labelStyle={'display': 'inline-block'},
                                id='invert-ecg-toggle'
                            )
                        ], className='six columns'),
                        html.Div([
                            html.A(
                                'Download RRs and classifications',
                                id='download-link',
                                download="",
                                href="",
                                target="_blank"
                            )
                        ], className='six columns'),
                    ], className='row')
                ], className='six columns'),
                html.Div([
                    html.Div([
                        html.Label('Select viewing length'),
                        dcc.Dropdown(
                            id='window-selection',
                            options=[
                                {'label': '15 s', 'value': '15 s'},
                                {'label': '1 min', 'value': '1 min'},
                                {'label': '3 min', 'value': '3 min'},
                                {'label': '5 min', 'value': '5 min'},
                                {'label': '10 min', 'value': '10 min'}
                            ],
                            value='None'
                        )
                    ]),
                ], className='six columns'),
            ], className="row"),
            html.Div([
                html.Div([
                    html.Label('Select file'),
                    dcc.Dropdown(
                        id='file_selection',
                        options=settings.file_options_list,
                        value=settings.file_options_list[0]['value']
                    )
                ])
            ])
        ], className='twelve columns'),
        html.Div([
            html.Div([
                html.Div([
                    html.Label("Navigation - move left and right"),
                    html.Button('<< Move left', id='move-left', style={'display': 'inline', 'width': '50%'}),
                    html.Button('Move right >>', id='move-right', style={'display': 'inline', 'width': '50%'})
                ], style={'margin-top': '10'})
            ], className='twelve columns')
        ], className='row'),

        html.Div([
            #    html.Div([
            dcc.Graph(id='ECG', config={'displayModeBar': False})
        ], style={'margin-top': '0'}),

        html.Div(id='second-line', children=[
            html.Div([
                html.Div([
                    dcc.Graph(id='RR-histogram')
                ])
            ], className='six columns'),
            html.Div([
                html.Div([
                    dcc.Graph(id='poincare-plot')
                ])

            ], className='six columns')
        ], className='row', style={'display': 'none'}),

        html.Div([
            html.Button('Save results', id='save-results', style={'display': 'inline', 'width': '50%'})
        ]),
        html.Div([
            html.P(id='saved-results-output')
        ]),
        html.Div([
            html.P(id="signal_RR_classification_change", children="")
        ]),

        html.Div([
            html.P(id="n_right_clicks", children="")
        ]),
        html.Div([
            html.P(id="n_left_clicks", children="")
        ]),
        html.Div([
            html.P(id="current_file", children="")
        ]),
        html.Div([
            html.P(id="invert-ecg", children="")
        ])
    ])


#def prepare_css(app):
#    # Dash CSS
#    app.css.append_css({
#        "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
    # Loading screen CSS
    # app.css.append_css({
    #    "external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})
