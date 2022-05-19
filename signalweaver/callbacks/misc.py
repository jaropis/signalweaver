from dash.dependencies import Input, Output

import io
import urllib.parse  # to help with the download part
import numpy as np

from app import app
from signalweaver.ecgs.manager import get_ecg


@app.callback(
    Output(component_id='download-link', component_property='download'),
    [Input(component_id='signal_RR_classification_change', component_property='children'),
     Input(component_id='current_file', component_property='children')]
)
def update_download_name(_, __):
    ecg = get_ecg()
    name = ecg.name[0:-4] + "_RR.txt"
    return name


@app.callback(
    Output(component_id='download-link', component_property='href'),
    [Input(component_id='signal_RR_classification_change', component_property='children'),
     Input(component_id='current_file', component_property='children')]
)
def update_download_link(_, __):
    ecg = get_ecg()
    rr_download = np.asarray([ecg.rr_intervals*1000, ecg.rr_annotations]).T
    text_buffer = io.BytesIO()  # creating a buffer - i do not want to use pandas, prefer buffering in memory
    np.savetxt(text_buffer, rr_download, fmt=['%5f', '%1d'],  # set it as a buffer for storing string in memory
               header='RRinterval\tannotation', delimiter='\t', newline='\n')
    rr_to_download = "data:text/csv;charset=utf-8," + \
                     urllib.parse.quote(text_buffer.getvalue().decode("utf-8").replace('# ', ''))  # there is a # as a
    # result of using byte strings in the results of the second line of this function, hence the above .replace
    return rr_to_download


@app.callback(
    Output(component_id='saved-results-output', component_property='children'),
    [Input(component_id='save-results', component_property='n_clicks')]
)
def save_results(click_in):
    if click_in is not None:
        ecg=get_ecg()
        ecg.update_results_dict()
        ecg.save_processed_data()
    return click_in

