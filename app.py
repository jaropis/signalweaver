import dash

app = dash.Dash(
    "SignalWeaver",
    title="SignalWeaver - ECG Analysis",
    update_title=None,  # Prevents "Updating..." from appearing in title
    external_stylesheets=[],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Professional ECG Signal Analysis Tool"},
    ]
)
#app = dash.Dash('auth')
app.server.secret_key = 'sdfasdsadsadaseqrfddfdfgrtbgbhgbnrt'
