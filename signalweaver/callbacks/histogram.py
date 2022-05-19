from dash.dependencies import Input, Output

from app import app
from signalweaver.ecgs.manager import get_ecg


@app.callback(
    Output(component_id="RR-histogram", component_property='figure'),
    [Input(component_id='signal_RR_classification_change', component_property='children'),
     Input(component_id='invert-ecg', component_property='children'),
     Input(component_id='current_file', component_property='children')]
)
def redraw_histogram_on_change(_, __, ___):
    ecg = get_ecg()
    return ecg.histogram()