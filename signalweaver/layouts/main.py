from dash import dcc, html
import settings

settings.init()
def prepare_layout(app):
    app.layout = html.Div(id='main-panel', children=[
        # New layout: Controls (including upload), Poincare plot, and Histogram each taking 1/3 width
        html.Div([
            html.Div([
                # Controls section (including upload)
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
                ]),
                html.Div([
                    html.Div([
                        dcc.Checklist(
                            options=[{'label': 'Invert ECG', 'value': 'Invert'}],
                            value=[],
                            labelStyle={'display': 'inline-block'},
                            id='invert-ecg-toggle'
                        )
                    ], className='twelve columns'),
                    html.Div([
                        html.A(
                            'Download RRs and classifications',
                            id='download-link',
                            download="",
                            href="",
                            target="_blank"
                        )
                    ], className='twelve columns'),
                ], className='row'),
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
                html.Div([
                    html.Label('Select file'),
                    dcc.Dropdown(
                        id='file_selection',
                        options=settings.file_options_list,
                        value=settings.file_options_list[0]['value']
                    )
                ])
            ], className='four columns'),
            html.Div([
                # Poincare plot in the middle
                dcc.Graph(id='poincare-plot')
            ], className='four columns'),
            html.Div([
                # RR histogram on the right
                dcc.Graph(id='RR-histogram')
            ], className='four columns')
        ], className='row'),
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
