from dash.dependencies import Input, Output

from app import app


# /plotting
@app.callback(
    Output(component_id='second-line', component_property='style'),
    [Input(component_id='second-row-toggle', component_property='value')]
)
def toggle_second_line(value):
    if 'Hide' in value:
        return {'display': 'none'}
    else:
        return {'display': 'block'}