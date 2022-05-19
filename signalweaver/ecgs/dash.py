import numpy as np

import plotly.graph_objs as go

from ..signal_classes import ECG

from ..signal_processing.ecg_processing import detect_r_waves

from .. HRAExplorer.signal_properties.RRclasses import RRSignal


# class DashECGSignal(ECG):
#     def __init__(self, file_path):
#         super().__init__(file_path)
#         self.n_right_clicks = 0
#         self.n_right_secondary_counter = 0
#         self.n_left_clicks = 0
#         self.n_left_secondary_counter = 0
#         self.change = 0
#         self.last_clicked_at = 0
#         self.window_length = 3000 * self.sampling_period  # this will be in seconds
#         self.position = self.get_initial_position()
#         self.first_peak_position = 0
#         self.offset_over_trace = + 0.05  # USE THIS WHILE CHANGING VIEWING WINDOW!!!
#         self.detection_window = int(0.05 / self.sampling_period)
#         self.inverted = False
#         self.number_of_lines = 1  # in how many lines the ECG trace is presented
#
#     def get_initial_position(self):
#         return self.time_track[0]
#
#     def get_current_time_track(self):
#         position = self.position - self.get_initial_position()
#         return self.time_track[int(position / self.sampling_period):
#                                int((position + self.window_length) /
#                                    self.sampling_period)]
#
#     def get_current_ecg_track(self):
#         position = self.position - self.get_initial_position()
#         return self.signal_values[int(position / self.sampling_period):
#                                   int((position + self.window_length) /
#                                       self.sampling_period)]
#
#     def get_current_peaks_positions(self, positions, values, get_first_peak=False):
#         """
#         returns the peaks located in the currently selected window
#         :param positions: the vector with the positions of the peaks (NN, supra, ventriculars)
#         :param values: the values of the peaks
#         :param get_first_peak: whether the position of the first peak is meaningful (it not always is, so set to default)
#         :return: the positions and values of the peaks in the viewing window, and either the first peak position or 0
#         """
#         condition = np.logical_and(
#             positions >= self.position,
#             positions < self.position + self.window_length)
#         try:
#             first_peak_position = 0 if not get_first_peak else np.where(condition == 1)[0][0]  # 1 represents True
#         except IndexError:
#             first_peak_position = None
#         return positions[condition], values[condition], first_peak_position
#
#     def step_right_left(self, n_clicked_right, n_clicked_left):
#         """
#         method moving the viewing window left - right on click
#         :param n_clicked_right: if >>move right<< was clicked
#         :param n_clicked_left: if >>move left<< was clicked
#         :return: None
#         """
#
#         if self.n_right_secondary_counter > self.n_right_clicks:
#             if self.position + 2 * self.window_length >= self.time_track[-1]:
#                 # why 2? because |---|--| - the first segment being window length. The plot is made from the
#                 # self.position calculated here until self.position + self.window_length. So in the situation like
#                 # above, I need to return position (middle bar) |--|---|, so that the last window fits exactly
#                 # the greater OR EQUAL is very important here
#                 self.position = self.time_track[-1] - self.window_length
#             else:
#                 self.position = self.position + self.window_length
#             self.n_right_clicks += 1
#
#         if self.n_left_secondary_counter > self.n_left_clicks:
#             if self.position - self.window_length < self.time_track[0]:
#                 self.position = self.time_track[0]
#             else:
#                 self.position = self.position - self.window_length
#             self.n_left_clicks += 1
#
#         return self.position # this is for testing purposes
#
#     def set_position_on_pp_click(self, click_data_PP):
#         """
#         the method sets the position of the viewing window after the PP click
#         :param click_data_PP: the click event data
#         :return: None
#         """
#         click_position = None if click_data_PP is None else click_data_PP['points'][0]['pointNumber']
#         if click_position is None:
#             return
#
#         # deciding whether to change default position on click
#         # click_data_PP remembers its current state
#         if self.last_clicked_at != click_position:
#             self.last_clicked_at = click_position
#             # we start counting from the position of the first r-wave, not from the first rr-interval, because
#             # the beginning is not present, unless there is an r-wave right at the beginning
#             # the following needs to be cumsummed instead [r_vaves_pos[0], self.rr_intervals[0:click_position]
#             # the first element in this vector is there because the part before first RR would not be represented
#             # otherwise
#             auxiliary_rr_time_track = np.cumsum( # to wyrazenie jest zle napisane!
#                 np.concatenate(
#                     (np.array((self.r_waves_all_pos[0],)),
#                      self.rr_intervals[0:(self.RRSignal.poincare.x_i_indices[click_position + 2])])
#                 )  # I am adding 2, because creating PP is like differentiating twice - first, R-waves are combined
#             )  # in pairs to form RR intervals, and then RR intervas are combined in pairs to form PP
#             clicked_at = np.where(
#                 np.array(self.time_track) ==  # the clicked poincare plot point
#                 auxiliary_rr_time_track[-1])[0][0] * self.sampling_period + self.time_track[0]  # have to add the
#             #  beginning of the time track, otherwise this method counts from zero
#
#             # centering viewing window on the clicked point, unless this is the beginning
#             self.position = (clicked_at if clicked_at < int(self.window_length / 2) else
#                              clicked_at - np.sum(self.RRSignal.poincare.xi[click_position + 2:click_position + 6]))
#             #  now the clicked RR will be fourth from the left
#
#     def update_window_length(self, window):
#         """
#         checks whether the user has changed the window length and updates if appropriate
#         :param window:
#         :return:
#         """
#         if (window is not None) and (window != self.window_length):
#             self.window_length = window * self.sampling_period
#
#     def insert_new_rr(self, ecg_click_position):
#         """
#         this function inserts a new r-wave  AND the corresponding annotation on click
#         :param ecg_click_position: clicked position in time units
#         :return: None
#         """
#         greater_rr_position = np.where(self.r_waves_all_pos > ecg_click_position)[0][0]
#         # finding the highest peak within 2*self.detection_window seconds of the click - there does not seem to be a
#         # dedicated method for this in numpy
#         clicked_index = np.where(self.time_track == ecg_click_position)[0][0]
#         ecg_segment = self.signal_values[clicked_index - self.detection_window:
#                                          clicked_index + self.detection_window]
#         relative_local_maximum = np.argmax(ecg_segment)
#         global_local_maximum = clicked_index - self.detection_window + relative_local_maximum
#
#         # checking if there already is an R-wave at the clicked position
#         # if there is, returning without changing anything
#         if abs(self.r_waves_all_pos[greater_rr_position - 1] - global_local_maximum) < 5 * self.sampling_period:
#             return False  # don't do anything
#         # inserting the r-wave
#         self.r_waves_all_pos = np.insert(self.r_waves_all_pos, greater_rr_position,
#                                          self.time_track[global_local_maximum])
#         self.r_waves_all_vals = np.insert(self.r_waves_all_vals, greater_rr_position,
#                                           self.signal_values[global_local_maximum])
#         # inserting the corresponding annotation
#         self.annotations = np.insert(self.annotations, greater_rr_position, 0)
#
#     def remove_rr(self, ecg_click_position):
#         """
#         this function removes a clicked r-wave AND the corresponding annotation on click
#         :param ecg_click_position: ecg_click_position: clicked position in time units
#         :return: None
#         """
#         exact_rr_position = np.where(self.r_waves_all_pos == ecg_click_position)[0][0]
#         self.r_waves_all_pos = np.delete(self.r_waves_all_pos, exact_rr_position)
#         self.r_waves_all_vals = np.delete(self.r_waves_all_vals, exact_rr_position)
#         self.annotations = np.delete(self.annotations, exact_rr_position)
#
#     def invert_ecg(self):
#         mean_ecg_value = np.mean(self.signal_values)
#         self.signal_values = -1 * (self.signal_values - mean_ecg_value) + mean_ecg_value
#         # and now repeating the constructor with the inverted ECG
#         self.update_state()
#
#     def update_state(self):
#         self.r_waves_all_pos, self.r_waves_all_vals = detect_r_waves(self.time_track, self.signal_values).T
#         self.annotations = self.annotate_r_waves()
#         self.ventriculars_pos, self.ventriculars_vals = self.get_ventriculars()
#         self.supraventriculars_pos, self.supraventriculars_vals = self.get_supraventriculars()
#         self.artifacts_pos, self.artifacts_vals = self.get_artifacts()
#         self.rr_intervals, self.rr_annotations = self.get_rrs()
#         self.update_poincare()
#
#     def update_poincare(self):
#         self.RRSignal = RRSignal([self.rr_intervals, self.rr_annotations], annotation_filter=(1, 2, 3))
#         self.RRSignal.set_poincare()
#
#     def ecg_and_peak_traces(self):
#         """
#         ths function takes data as a pandas dataframe, starting position, window length
#         and extracts the time_track, voltage, the time-positions of the peaks and the peak
#         values. It returns two Dash tracks which are then used for the figure creation
#         """
#         ############################################################################################################
#         # Here is a strange place - this is at this point that I set the object property "self.first_peak_position #
#         # this is the index of the first r_wave in the analyzed window. In this way the object will be able to     #
#         # calculate which r_wave exactly was clicked and will change its annotation by adding the first r_wave po-#
#         # sition.                                                                                                  #
#         ############################################################################################################
#
#         x_r_waves, y_r_waves, self.first_peak_position = self.get_current_peaks_positions(self.r_waves_all_pos,
#                                                                                           self.r_waves_all_vals, True)
#         x_ventriculars, y_ventriculars, _ = self.get_current_peaks_positions(*self.get_ventriculars())
#         x_supraventriculars, y_supraventriculars, _ = self.get_current_peaks_positions(*self.get_supraventriculars())
#         x_artifacts, y_artifacts, _ = self.get_current_peaks_positions(*self.get_artifacts())
#         return {'data': [go.Scatter(
#             x=self.get_current_time_track(), y=self.get_current_ecg_track(),
#             mode='lines',
#             line=dict(color='black'),
#             name="ECG trace",
#         ),
#             go.Scatter(
#                 x=x_r_waves,
#                 y=y_r_waves + self.offset_over_trace,
#                 mode='markers',
#                 marker=dict(size=12, color='green'),
#                 name='Detected R-peaks'
#             ),
#             go.Scatter(
#                 x=x_ventriculars,
#                 y=y_ventriculars + self.offset_over_trace,
#                 mode='markers',
#                 marker=dict(size=12, color='blue'),
#                 name='Detected ven.'
#             ),
#             go.Scatter(
#                 x=x_supraventriculars,
#                 y=y_supraventriculars + self.offset_over_trace,
#                 mode='markers',
#                 marker=dict(size=12, color='magenta'),
#                 name='Detected sup.'
#             ),
#             go.Scatter(
#                 x=x_artifacts,
#                 y=y_artifacts + self.offset_over_trace,
#                 mode='markers',
#                 marker=dict(size=12, color='red'),
#                 name='Detected art.'
#             )
#         ],
#             'layout': go.Layout(
#                 title="Example R-wave detection",
#                 hovermode='closest')}
#
#     def poincare_plot(self):
#         return {'data': [go.Scatter(
#             x=self.RRSignal.poincare.xi,
#             y=self.RRSignal.poincare.xii,
#             mode='markers',
#             marker=dict(size=12, color='black', opacity='0.2'),
#             name='Poincare plot'
#         )],
#             'layout': go.Layout(
#                 title="Poincare plot<br>(<i>toggle off for faster scrolling</i>)",
#                 hovermode='closest'
#             )}
#
#     def histogram(self):
#         return {'data': [go.Histogram(
#             x=self.rr_intervals,
#             histnorm='probability',
#             name='Histogram of RR intervals'
#         )],
#             'layout': go.Layout(
#                 title="Histogram of RR intervals <br>(<i>toggle off for faster scrolling</i>)",
#                 hovermode='closest'
#             )
#         }
