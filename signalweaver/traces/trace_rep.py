import numpy as np

import plotly.graph_objs as go

from ..signal_classes import ECG

POSSIBLE_WINDOWS = {'15 s': 15, '1 min': 60, '3 min': 3 * 60, '5 min': 5 * 60, '10 min': 10 * 60}
POSSIBLE_LINE_No = {'15 s': 1, '1 min': 3, '3 min': 5, '5 min': 10, '10 min': 20}
POSSIBLE_LINE_HEIGHTS = {'15 s': 4, '1 min': 2, '3 min': 1.5, '5 min': 1, '10 min': 0.8}
PHYSICAL_LINE_HEIGHT = 100


class TraceECGSignal(ECG):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.n_right_clicks = 0
        self.n_right_secondary_counter = 0
        self.n_left_clicks = 0
        self.n_left_secondary_counter = 0
        self.change = 0
        self.last_clicked_at = 0
        self.position = self.get_initial_position()
        self.first_peak_position = 0
        self.offset_over_trace = + 0.05  # USE THIS WHILE CHANGING VIEWING WINDOW!!!
        self.detection_window = int(0.05 / self.sampling_period)
        self.inverted = False
        self.window_length, self.number_of_lines, self.single_line_height = self.get_initial_window()
        # Calculate and store initial Poincare plot ranges
        self._calculate_initial_poincare_ranges()

    def get_initial_position(self):
        return self.time_track[0]

    def get_initial_window(self):
        if len(self.time_track) * self.sampling_period <= POSSIBLE_WINDOWS['15 s']:
            self.window_length = len(self.time_track) * self.sampling_period
            self.number_of_lines = POSSIBLE_LINE_No['15 s']
            self.single_line_height = POSSIBLE_LINE_HEIGHTS['15 s']
        if POSSIBLE_WINDOWS['15 s'] < len(self.time_track) * self.sampling_period <= POSSIBLE_WINDOWS['1 min']:
            self.window_length = POSSIBLE_WINDOWS['15 s']
            self.number_of_lines = POSSIBLE_LINE_No['15 s']
            self.single_line_height = POSSIBLE_LINE_HEIGHTS['15 s']
        if POSSIBLE_WINDOWS['1 min'] < len(self.time_track) * self.sampling_period <= POSSIBLE_WINDOWS['5 min']:
            self.window_length = POSSIBLE_WINDOWS['1 min']
            self.number_of_lines = POSSIBLE_LINE_No['1 min']
            self.single_line_height = POSSIBLE_LINE_HEIGHTS['1 min']
        if POSSIBLE_WINDOWS['5 min'] < len(self.time_track) * self.sampling_period:
            self.window_length = POSSIBLE_WINDOWS['5 min']
            self.number_of_lines = POSSIBLE_LINE_No['5 min']
            self.single_line_height = POSSIBLE_LINE_HEIGHTS['5 min']
        return self.window_length, self.number_of_lines, self.single_line_height

    def _calculate_initial_poincare_ranges(self):
        """
        Calculate and store the initial axis ranges for the Poincare plot based on the full dataset.
        This ensures the plot doesn't jump when data points are filtered out.
        """
        x_data = self.RRSignal.poincare.xi
        y_data = self.RRSignal.poincare.xii
        min_val = min(min(x_data), min(y_data))
        max_val = max(max(x_data), max(y_data))
        self.poincare_range_start = max(0, min_val - (max_val - min_val) * 0.05)  # Start from 0 or slightly below min
        self.poincare_range_end = max_val + (max_val - min_val) * 0.05  # Add small margin

    def _format_time_for_tooltip(self, time_in_seconds):
        """
        Format time for tooltips based on duration:
        - Under 1 minute: show only seconds
        - 1 minute to 1 hour: show minutes and seconds
        - Over 1 hour: show hours, minutes and seconds
        """
        if time_in_seconds < 60:
            return f"{time_in_seconds:.3f} s"
        elif time_in_seconds < 3600:
            minutes = int(time_in_seconds // 60)
            seconds = time_in_seconds % 60
            return f"{minutes}:{seconds:06.3f}"
        else:
            hours = int(time_in_seconds // 3600)
            minutes = int((time_in_seconds % 3600) // 60)
            seconds = time_in_seconds % 60
            return f"{hours}:{minutes:02d}:{seconds:06.3f}"

    def get_current_time_track(self):
        position = self.position - self.get_initial_position()
        return self.time_track[int(position / self.sampling_period):
                               int((position + self.window_length) /
                                   self.sampling_period)]

    def get_current_ecg_track(self):
        position = self.position - self.get_initial_position()
        return self.signal_values[int(position / self.sampling_period):
                                  int((position + self.window_length) /
                                      self.sampling_period)]

    def get_current_peaks_positions(self, positions, values, get_first_peak=False):
        """
        returns the peaks located in the currently selected window
        :param positions: the vector with the positions of the peaks (NN, supra, ventriculars)
        :param values: the values of the peaks
        :param get_first_peak: whether the position of the first peak is meaningful (it not always is, so set to default)
        :return: the positions and values of the peaks in the viewing window, and either the first peak position or 0
        """
        condition = np.logical_and(
            positions >= self.position,
            positions < self.position + self.window_length)
        try:
            first_peak_position = 0 if not get_first_peak else np.where(condition == 1)[0][0]  # 1 represents True
        except IndexError:
            first_peak_position = None
        return positions[condition], values[condition], first_peak_position

    def step_right_left(self, n_clicked_right, n_clicked_left):
        """
        method moving the viewing window left - right on click
        :param n_clicked_right: if >>move right<< was clicked
        :param n_clicked_left: if >>move left<< was clicked
        :return: None
        """

        if self.n_right_secondary_counter > self.n_right_clicks:
            if self.position + 2 * self.window_length >= self.time_track[-1]:
                # why 2? because |---|--| - the first segment being window length. The plot is made from the
                # self.position calculated here until self.position + self.window_length. So in the situation like
                # above, I need to return position (middle bar) |--|---|, so that the last window fits exactly
                # the greater OR EQUAL is very important here
                self.position = self.time_track[-1] - self.window_length
            else:
                self.position = self.position + self.window_length
            self.n_right_clicks += 1

        if self.n_left_secondary_counter > self.n_left_clicks:
            if self.position - self.window_length < self.time_track[0]:
                self.position = self.time_track[0]
            else:
                self.position = self.position - self.window_length
            self.n_left_clicks += 1
        self.update_results_dict()
        self.save_processed_data()
        return self.position  # this is for testing purposes

    def set_position_on_pp_click(self, click_data_PP):
        """
        the method sets the position of the viewing window after the PP click
        :param click_data_PP: the click event data
        :return: None
        """
        click_position = None if click_data_PP is None else click_data_PP['points'][0]['pointNumber']
        if click_position is None:
            return
        # UWAGA! Trzeba przepisac czym jest Poincare plot - nie moze byc tak jak jest w linijce 131, ze rr_intervals
        # jest indeksowane przez poincare.x_i_indices, bo te indeksy maja pousuwane elementy - trzeba samemu zrobic
        # Poincare plot, taki, ktory zachowywalby wszystkie indeksy, ale nie wszystko pokazywal

        # deciding whether to change default position on click
        # click_data_PP remembers its current state
        if self.last_clicked_at != click_position:
            self.last_clicked_at = click_position
            # we start counting from the position of the first r-wave, not from the first rr-interval, because
            # the beginning is not present, unless there is an r-wave right at the beginning
            # the following needs to be  ummed instead [r_waves_pos[0], self.rr_intervals[0:click_position]
            # the first element in this vector is there because the part before first RR would not be represented
            # otherwise
            auxiliary_rr_time_track = np.cumsum(
                np.concatenate(
                    (np.array((self.r_waves_all_pos[0],)),
                     self.rr_intervals[0:(self.RRSignal.poincare.x_i_indices[click_position + 2])])
                )  # I am adding 2, because creating PP is like differentiating twice - first, R-waves are combined
            )  # in pairs to form RR intervals, and then RR intervals are combined in pairs to form PP
            clicked_at = np.where(
                np.array(self.time_track) ==  # the clicked poincare plot point
                auxiliary_rr_time_track[-1])[0][0] * self.sampling_period + self.time_track[0]  # have to add the
            #  beginning of the time track, otherwise this method counts from zero

            # centering viewing window on the clicked point, unless this is the beginning or too close to the end
            if clicked_at < np.sum(self.RRSignal.poincare.xi[click_position + 2:click_position + 6]):
                self.position = clicked_at
            elif clicked_at + self.window_length / self.sampling_period >= len(self.time_track):
                self.position = self.time_track[-1] - self.window_length
            else:
                self.position = clicked_at - np.sum(self.RRSignal.poincare.xi[click_position + 2:click_position + 6])
            #  now the clicked RR will be fourth from the left - to understand why I use 2 and 6 see
            #  the comment above

    def update_window_length(self, window):
        """
        checks whether the user has changed the window length and updates if appropriate
        :param window:
        :return:
        """
        if (window is not None) and (window != self.window_length) and window != "None":
            if len(self.time_track) * self.sampling_period < POSSIBLE_WINDOWS.get(window):
                # get lost and change nothing
                return
            # remember, window_length is in seconds
            # if self.position + new window is beyond the end of the recording, set a new position, so that one window
            # fits
            if self.position + POSSIBLE_WINDOWS.get(window) > len(self.time_track) * self.sampling_period + \
                    self.time_track[0]:
                self.position = len(self.time_track) * self.sampling_period + self.time_track[0] - POSSIBLE_WINDOWS.get(
                    window)
            self.window_length = POSSIBLE_WINDOWS.get(window)
            self.number_of_lines = POSSIBLE_LINE_No.get(window)
            self.single_line_height = POSSIBLE_LINE_HEIGHTS.get(window)
        if self.window_length is None:
            self.get_initial_window()

    def insert_new_rr(self, ecg_click_position, ignore_radius=15):
        """
        this function inserts a new r-wave  AND the corresponding annotation on click
        :param ecg_click_position: clicked position in time units
        :ignore_radius: the radius within which a click will be ignored
        :return: None
        """
        greater_rr_position = np.where(self.r_waves_all_pos > ecg_click_position)[0][0]
        # finding the highest peak within 2*self.detection_window seconds of the click - there does not seem to be a
        # dedicated method for this in numpy
        clicked_index = np.where(self.time_track >= ecg_click_position)[0][0]
        ecg_segment = self.signal_values[clicked_index - self.detection_window:
                                         clicked_index + self.detection_window]
        relative_local_maximum = np.argmax(ecg_segment)
        global_local_maximum = clicked_index - self.detection_window + relative_local_maximum
        # checking if there already is an R-wave at the clicked position
        # if there is, returning without changing anything
        # print(greater_rr_position)
        # print(abs(self.r_waves_all_pos[
        #           greater_rr_position - 1]/self.sampling_period - global_local_maximum), ignore_radius)
        if abs(self.r_waves_all_pos[
                   greater_rr_position - 1]/self.sampling_period - global_local_maximum) < ignore_radius or abs(self.r_waves_all_pos[
                   greater_rr_position]/self.sampling_period - global_local_maximum) < ignore_radius:
            # print("move along, nothing to see")
            return False  # don't do anything
        # inserting the r-wave
        low = greater_rr_position - 2 if greater_rr_position - 2 > 0 else 0
        high = greater_rr_position + 2 if greater_rr_position + 2 < len(self.r_waves_all_pos) else len(self.r_waves_all_pos)

        self.r_waves_all_pos = np.insert(self.r_waves_all_pos, greater_rr_position,
                                         self.time_track[global_local_maximum])
        self.r_waves_all_vals = np.insert(self.r_waves_all_vals, greater_rr_position,
                                          self.signal_values[global_local_maximum])
        # inserting the corresponding annotation
        self.annotations = np.insert(self.annotations, greater_rr_position, 0)
        return True

    def remove_rr(self, ecg_click_position):
        """
        this function removes a clicked r-wave AND the corresponding annotation on click
        :param ecg_click_position: ecg_click_position: clicked position in time units
        :return: None
        """
        exact_rr_position = np.where(self.r_waves_all_pos >= ecg_click_position)[0][0]
        self.r_waves_all_pos = np.delete(self.r_waves_all_pos, exact_rr_position)
        self.r_waves_all_vals = np.delete(self.r_waves_all_vals, exact_rr_position)
        self.annotations = np.delete(self.annotations, exact_rr_position)

        # now see what the next one is and, if it is 0 and the RR is too large, annotate it as artifact
        #if not (self.rr_filter[0] < self.r_waves_all_pos[exact_rr_position] - self.r_waves_all_pos[exact_rr_position-1] < self.rr_filter[1]):
        #    self.annotations[exact_rr_position] = 3

    def folded_indices(self, vector, down, up, starting_sample):
        """
        method used for folding the markered signals (vent, supra, artif)
        :param vector: vector to fold
        :param down: lower boundary
        :param up: upper boundary
        :param starting_sample: the sample from which the folding starts
        :return: boolean vector - true corresponds to present fold
        """
        try:
            folded_ind = (np.logical_and(vector >= down * self.sampling_period + starting_sample,
                                         vector < up * self.sampling_period + starting_sample))
        except IndexError as e:
            print(e)
        return folded_ind

    def fold_figure(self, time, ecg, x_r_waves, y_r_waves, x_ventriculars, y_ventriculars, x_supraventriculars,
                    y_supraventriculars,
                    x_artifacts, y_artifacts):
        local_win_length = int((self.window_length / self.sampling_period) / self.number_of_lines)
        starting_sample = time[0]
        figure = {}
        data = []
        line_shift = self.single_line_height * 3 / 2
        for idx in range(self.number_of_lines):
            # line indices are numerical
            line_indices_down, local_indices_up = idx * local_win_length, (idx + 1) * local_win_length
            current_x_shift = time[line_indices_down:local_indices_up][0] - starting_sample

            # now the scaling needs to be calculated, so that every ecg line fits in a separate display line - this
            # scaling needs to be applied to all signals here

            y_baseline = np.min(ecg[line_indices_down:local_indices_up])
            y_max = np.max(ecg[line_indices_down:local_indices_up] - y_baseline)
            data.extend([
                go.Scatter(
                    x=time[line_indices_down:local_indices_up] - current_x_shift,
                    y=(ecg[line_indices_down:local_indices_up] - y_baseline) / y_max - idx * line_shift,
                    mode='lines',
                    line=dict(color='black'),
                    name="ECG trace",
                    hovertemplate='<extra></extra>'
                ),
                go.Scatter(
                    x=x_r_waves[self.folded_indices(x_r_waves, line_indices_down, local_indices_up,
                                                    starting_sample)] - current_x_shift,
                    y=(y_r_waves[
                           self.folded_indices(x_r_waves, line_indices_down, local_indices_up,
                                               starting_sample)] - y_baseline) / y_max +
                      self.offset_over_trace - idx * line_shift,
                    mode='markers',
                    marker=dict(size=12, color='green'),
                    name='Detected R-peaks',
                    customdata=[self._format_time_for_tooltip(t) for t in x_r_waves[self.folded_indices(x_r_waves, line_indices_down, local_indices_up, starting_sample)] - current_x_shift],
                    hovertemplate='<b>Normal beat</b><br>' +
                                 'Time: %{customdata}<br>' +
                                 '<extra></extra>'
                ),
                go.Scatter(
                    x=x_ventriculars[self.folded_indices(x_ventriculars, line_indices_down, local_indices_up,
                                                         starting_sample)] - current_x_shift,
                    y=(y_ventriculars[self.folded_indices(x_ventriculars, line_indices_down,
                                                          local_indices_up,
                                                          starting_sample)] - y_baseline) / y_max + self.offset_over_trace - idx * line_shift,
                    mode='markers',
                    marker=dict(size=12, color='blue'),
                    name='Detected ven.',
                    customdata=[self._format_time_for_tooltip(t) for t in x_ventriculars[self.folded_indices(x_ventriculars, line_indices_down, local_indices_up, starting_sample)] - current_x_shift],
                    hovertemplate='<b>Ventricular beat</b><br>' +
                                 'Time: %{customdata}<br>' +
                                 '<extra></extra>'
                ),
                go.Scatter(
                    x=x_supraventriculars[
                          self.folded_indices(x_supraventriculars, line_indices_down, local_indices_up,
                                              starting_sample)] - current_x_shift,
                    y=(y_supraventriculars[self.folded_indices(x_supraventriculars, line_indices_down,
                                                               local_indices_up,
                                                               starting_sample)] - y_baseline) / y_max + self.offset_over_trace - idx * line_shift,
                    mode='markers',
                    marker=dict(size=12, color='magenta'),
                    name='Detected sup.',
                    customdata=[self._format_time_for_tooltip(t) for t in x_supraventriculars[self.folded_indices(x_supraventriculars, line_indices_down, local_indices_up, starting_sample)] - current_x_shift],
                    hovertemplate='<b>Supraventricular beat</b><br>' +
                                 'Time: %{customdata}<br>' +
                                 '<extra></extra>'
                ),
                go.Scatter(
                    x=x_artifacts[self.folded_indices(x_artifacts, line_indices_down, local_indices_up,
                                                      starting_sample)] - current_x_shift,
                    y=(y_artifacts[self.folded_indices(x_artifacts, line_indices_down,
                                                       local_indices_up,
                                                       starting_sample)] - y_baseline) / y_max + self.offset_over_trace - idx * line_shift,
                    mode='markers',
                    marker=dict(size=12, color='red'),
                    name='Detected art.',
                    customdata=[self._format_time_for_tooltip(t) for t in x_artifacts[self.folded_indices(x_artifacts, line_indices_down, local_indices_up, starting_sample)] - current_x_shift],
                    hovertemplate='<b>Artifact</b><br>' +
                                 'Time: %{customdata}<br>' +
                                 '<extra></extra>'
                )
            ])
        figure['data'] = data
        figure['layout'] = go.Layout(
            hovermode='closest',
            height=self.number_of_lines * self.single_line_height * PHYSICAL_LINE_HEIGHT,
            # yaxis=dict(range=[- 0.5 * self.single_line_height - idx * line_shift, self.single_line_height]),
            showlegend=False,
            margin=dict(
                l=50,
                r=50,
                b=100,
                t=10,
                pad=4
            )
        )
        return figure

    def unfold_click_data(self, click_data_rr):
        if click_data_rr is not None:
            line_number = np.floor(click_data_rr['points'][0][
                                       'curveNumber'] / 5)  # this is the number of the ECG lines on screen, not curve number
            click_data_rr['points'][0]['curveNumber'] = click_data_rr['points'][0]['curveNumber'] % 5
            click_data_rr['points'][0]['x'] = click_data_rr['points'][0]['x'] + line_number * np.ceil(
                self.window_length / self.number_of_lines)
        return click_data_rr

    def ecg_and_peak_traces(self):
        """
        ths function takes data as a pandas dataframe, starting position, window length
        and extracts the time_track, voltage, the time-positions of the peaks and the peak
        values. It returns two Dash tracks which are then used for the figure creation
        """
        ############################################################################################################
        # Here is a strange place - this is at this point that I set the object property "self.first_peak_position #
        # this is the index of the first r_wave in the analyzed window. In this way the object will be able to     #
        # calculate which r_wave exactly was clicked and will change its annotation by adding the first r_wave po-#
        # sition.                                                                                                  #
        ############################################################################################################
        x_r_waves, y_r_waves, self.first_peak_position = self.get_current_peaks_positions(self.r_waves_all_pos,
                                                                                          self.r_waves_all_vals, True)
        x_ventriculars, y_ventriculars, _ = self.get_current_peaks_positions(*self.get_ventriculars())
        x_supraventriculars, y_supraventriculars, _ = self.get_current_peaks_positions(*self.get_supraventriculars())
        x_artifacts, y_artifacts, _ = self.get_current_peaks_positions(*self.get_artifacts())
        time = self.get_current_time_track()
        ecg_trace = self.get_current_ecg_track()
        return self.fold_figure(time, ecg_trace, x_r_waves, y_r_waves, x_ventriculars, y_ventriculars,
                                x_supraventriculars,
                                y_supraventriculars, x_artifacts, y_artifacts)

    def poincare_plot(self):
        # Use the stored ranges calculated at initialization
        x_data = self.RRSignal.poincare.xi
        y_data = self.RRSignal.poincare.xii
        
        # Calculate plot size to maintain 1:1 aspect ratio - larger size for expanded layout
        plot_size = 700  # Increased base size in pixels for the larger container
        
        return {'data': [go.Scattergl(
            x=x_data,
            y=y_data,
            mode='markers',
            marker=dict(size=12, color='black', opacity=0.2),
            name='Poincare plot',
            hovertemplate='<b>RR<sub>i</sub></b>: %{x:.3f} s<br>' +
                         '<b>RR<sub>i+1</sub></b>: %{y:.3f} s<br>' +
                         '<extra></extra>'
        )],
            'layout': go.Layout(
                title="Poincare plot",
                hovermode='closest',
                width=plot_size,
                height=plot_size,
                xaxis=dict(
                    title='RR<sub>i</sub>',
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    range=[0, self.poincare_range_end],
                    constraintoward='left'
                ),
                yaxis=dict(
                    title='RR<sub>i+1</sub>',
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    range=[0, self.poincare_range_end],
                    constraintoward='bottom'
                )
            )}


