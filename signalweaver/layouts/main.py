from dash import dcc, html
import settings

settings.init()
def prepare_layout(app):
    app.layout = html.Div(id='main-panel', children=[
        # Header section
        html.Div([
            html.H1("⚡ Signal Weaver", className="text-center mb-3"),
            html.P("Advanced ECG Signal Analysis Platform", className="text-center text-light mb-2")
        ], className="row"),
        
        # New layout: Controls (including upload), Poincare plot, and Histogram each taking 1/3 width
        html.Div([
            html.Div([
                # Controls section (including upload)
                html.H3("⚙️ Controls", className="section-header"),
                # html.Div([
                #     dcc.Upload(
                #         id='upload-data',
                #         children=html.Div([
                #             'Drag and Drop or',
                #             html.A(' Select Files')
                #         ]),

                #         style={
                #             'width': '100%',
                #             'height': '60px',
                #             'lineHeight': '60px',
                #             'borderWidth': '1px',
                #             'borderStyle': 'dashed',
                #             'borderRadius': '5px',
                #             'textAlign': 'center',
                #             'margin': '10px'
                #         },
                #         # Allow multiple files to be uploaded
                #         multiple=False
                #     )
                # ]),
                html.Div([
                    html.Div([
                        dcc.Checklist(
                            options=[{'label': 'Invert ECG', 'value': 'Invert'}],
                            value=[],
                            labelStyle={'display': 'flex', 'align-items': 'center', 'gap': '8px'},
                            id='invert-ecg-toggle',
                            className='checklist-container'
                        )
                    ], className='twelve columns mb-2'),
                    html.Div([
                        html.A(
                            'Download RRs and classifications',
                            id='download-link',
                            download="",
                            href="",
                            target="_blank"
                        )
                    ], className='twelve columns mb-2'),
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
                        value='10 min'
                    )
                ], className="mb-2"),
                html.Div([
                    html.Label('Select file'),
                    dcc.Dropdown(
                        id='file_selection',
                        options=settings.file_options_list,
                        value=settings.file_options_list[0]['value']
                    )
                ], className="mb-2")
            ], className='four columns'),
            html.Div([
                # Poincare plot taking more space
                html.H3("📊 Poincaré Plot", className="section-header"),
                dcc.Graph(id='poincare-plot')
            ], className='eight columns')
        ], className='row'),
        # Navigation section
        html.Div([
            html.Div([
                html.H3("🧭 Navigation", className="section-header"),
                html.Div([
                    html.Label("Navigate through the signal", className="mb-1"),
                    html.Div([
                        html.Button('← Move Left', id='move-left'),
                        html.Button('Move Right →', id='move-right')
                    ], className='button-container')
                ])
            ], className='twelve columns')
        ], className='row'),

        # ECG Plot section
        html.Div([
            html.H3("💓 ECG Signal", className="section-header"),
            dcc.Graph(id='ECG', config={'displayModeBar': False})
        ], className='row'),

        # Actions section
        html.Div([
            html.Div([
                html.H3("🎯 Actions", className="section-header"),
                html.Button('💾 Save Results', id='save-results', className="button-primary")
            ], className='six columns'),
            html.Div([
                html.H3("📋 Status", className="section-header"),
                html.P(id='saved-results-output', className="status-indicator")
            ], className='six columns')
        ], className='row'),
        # Hidden elements for debugging/state
        html.Div([
            html.P(id="signal_RR_classification_change", children="", style={'display': 'none'}),
            html.P(id="n_right_clicks", children="", style={'display': 'none'}),
            html.P(id="n_left_clicks", children="", style={'display': 'none'}),
            html.P(id="current_file", children="", style={'display': 'none'}),
            html.P(id="invert-ecg", children="", style={'display': 'none'})
        ])
    ])


#def prepare_css(app):
#    # Dash CSS
#    app.css.append_css({
#        "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
    # Loading screen CSS
    # app.css.append_css({
    #    "external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})
