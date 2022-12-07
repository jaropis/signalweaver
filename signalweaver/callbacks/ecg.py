import base64  # to help with the upload part
import io
import numpy as np
from dash.dependencies import Input, Output, State

from app import app
from signalweaver.ecgs.manager import add_ecg, get_ecg
from signalweaver.dash_files.dash_rep import DashECGSignal

# @app.callback(
#     Output(component_id='current_file', component_property='children'),
#     [Input(component_id='upload-data', component_property='contents'),
#      Input(component_id='upload-data', component_property='filename'),
#      Input(component_id='upload-data', component_property='last_modified')]
# )
# def uploaded_new_ecg(contents, filename, last_modified):
#     if contents:
#         try:
#             content_type, content_string = contents.split(',') # w contents mamy najpierw data:text/csv;base64 potem przecinek, a potem zakodowana zawartosc pliku - chwytamy te zawartosc i rozkodowujemy
#             decoded = base64.b64decode(content_string)
#             ecg = DashECGSignal(io.StringIO(decoded.decode('utf-8')))
#             ecg.name = filename
#             add_ecg(filename)
#             return filename
#         except Exception as e:
#             print(e)
#
#     return ""
#

@app.callback(
    Output(component_id='current_file', component_property='children'),
    [Input(component_id='file_selection', component_property='value')]
)
def selected_new_ecg(file_path):
    ecg = DashECGSignal(file_path)
    ecg.name = file_path
    add_ecg(file_path)
    return(file_path.split("/")[0])


@app.callback(
    Output(component_id='invert-ecg', component_property='children'),
    [Input(component_id='invert-ecg-toggle', component_property='value')]
)
def invert_ecg(value):
    ecg = get_ecg()
    if 'Invert' in value: # this one soooo needs refactoring
        print("pierwsza")
        ecg.invert_ecg()
        return 'change'
    else:
        if ecg.inverted:
            ecg.invert_ecg()
        return 'none'


@app.callback(
    Output(component_id='n_right_clicks', component_property="children"),
    [Input(component_id='move-right', component_property='n_clicks')]
)
def update_n_right_clicks(n_right_clicks):
    """
    n_clicks reset from time to time and ECG jumps around, so they will be kept in session inside the signalling div
    :param n_right_clicks: n_clicks from the right button, basically "whether right button was clicked"
    :return: either the new position (after click) or old position if n_click is None at refresh
    """
    ecg = get_ecg()
    # do not exceed the length of the recording (mind the inequality - it has to be sharp! or the plot will oscillate)
    if n_right_clicks is not None and ecg.position + ecg.window_length < ecg.time_track[-1]:
        ecg.n_right_secondary_counter += 1
    return ecg.n_right_secondary_counter


@app.callback(
    Output(component_id='n_left_clicks', component_property="children"),
    [Input(component_id='move-left', component_property='n_clicks')]
)
def update_n_left_clicks(n_left_clicks):
    """
    n_clicks reset from time to time and ECG jumps around, so they will be kept in session inside the signalling div
    :param n_left_clicks: n_clicks from the left button, basically "whether left button was clicked"
    :return: either the new position (after click) or old position if n_click is None at refresh
    """
    ecg = get_ecg()
    # do not go beyond the beginning of the recording
    if n_left_clicks is not None and ecg.position > ecg.time_track[0]:
        # this is because in another part ecg.position is set to exactly ecg.time_track[0]
        ecg.n_left_secondary_counter += 1
    return ecg.n_left_secondary_counter

@app.callback(
    Output(component_id='ECG', component_property='figure'),
    [Input(component_id='n_right_clicks', component_property='children'),
     Input(component_id='n_left_clicks', component_property='children'),
     Input(component_id='poincare-plot', component_property='clickData'),
     Input(component_id='signal_RR_classification_change', component_property='children'),
     Input(component_id='current_file', component_property='children'),
     Input(component_id='invert-ecg', component_property='children'),
     Input(component_id='window-selection', component_property="value")]
)
def on_right_left_peak_or_pp_click(n_clicked_right=10000, n_clicked_left=10000, click_data=None,
                                   peak_classification_change=None, current_file="",
                                   invert_ecg="none", window=None):
    """
    this function listens to right-left clicked events and updates position
    the two assignments below are there to avoid None type at the start
    :param n_clicked_right: >>right<< button click Dash counter
    :param n_clicked_left: >>left<< button click Dash counter
    :param click_data: Dash clickData object
    :param peak_classification_change: signal from the hidden div that something was clicked on the ECG-trace
    :param window: value from the "window" form, indicating the new(?) window length
    :return: plotly figure with ECG and annotations traces
    """

    ecg = get_ecg()
    window = window or ecg.window_length
    # check if window length has changed and if so, update
    ecg.update_window_length(window)

    # decide whether to move right or left by one window length
    ecg.step_right_left(int(n_clicked_right) if n_clicked_right != '' else 0, int(n_clicked_left) if n_clicked_left != '' else 0)
    # now deciding whether anything has been clicked on the poincare plot
    ecg.set_position_on_pp_click(click_data)
    return ecg.ecg_and_peak_traces()


@app.callback(
    Output(component_id='signal_RR_classification_change', component_property='children'),
    [Input(component_id='ECG', component_property='clickData')]
 )
def update_rr_classification_on_click(click_data_rr):
    ecg = get_ecg()
    click_data_rr = ecg.unfold_click_data(click_data_rr)

    def get_click_index(clicked_data):
        positions, _, _ = ecg.get_current_peaks_positions(ecg.r_waves_all_pos, ecg.r_waves_all_vals)
        peak_position = np.argmin(np.abs(positions - clicked_data['points'][0]['x']))
        return peak_position

    if click_data_rr is not None:
        change = False
        clicked_at = get_click_index(click_data_rr) + ecg.first_peak_position
        if click_data_rr['points'][0]['curveNumber'] == 1:
            ecg.annotations[clicked_at] = 1
            change = True
        if click_data_rr['points'][0]['curveNumber'] == 2:
            ecg.annotations[clicked_at] = 2
            change = True
        if click_data_rr['points'][0]['curveNumber'] == 3:
            ecg.annotations[clicked_at] = 3
            change = True
        if click_data_rr['points'][0]['curveNumber'] == 4:
            ecg.remove_rr(click_data_rr['points'][0]['x'])
            change = True
        if click_data_rr['points'][0]['curveNumber'] == 0:
            change = ecg.insert_new_rr(click_data_rr['points'][0]['x'])
            # print(change)
        if change:
            ecg.ventriculars_pos, ecg.ventriculars_vals = ecg.get_ventriculars()
            ecg.supraventriculars_pos, ecg.supraventriculars_vals = ecg.get_supraventriculars()
            ecg.artifacts_pos, ecg.artifacts_vals = ecg.get_artifacts()
            ecg.rr_intervals, ecg.rr_annotations = ecg.get_rrs()  # update rr intervals
            ecg.update_poincare()
            ecg.update_results_dict()  # since above some vectors were rebinded, and some need to be recalculated,
            # there will be problem when saving, so the resulting dictionary needs to be updated
            ecg.change += 1
            return ecg.change
        else:
            return ecg.change
    else:
        return ecg.change
