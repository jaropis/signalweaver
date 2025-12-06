import unittest
from signalweaver import TraceECGSignal


class TestNavigation(unittest.TestCase):

    def setUp(self):
        name = '2017MEN_001rest.csv'
        self.trace_signal = TraceECGSignal(name)

    def test_move_right(self):
        self.trace_signal.position = 0
        self.trace_signal.n_right_secondary_counter = 1 # clicked once
        self.assertTrue(self.trace_signal.step_right_left(0, 0) == self.trace_signal.window_length)

    def test_end_right_move(self):
        """
        testing if a move at the end results in setting the position to lenght - window
        """
        local_window_length = 3000
        self.trace_signal.window_length = local_window_length
        self.trace_signal.position = len(self.trace_signal.time_track) - 2 * self.trace_signal.window_length + local_window_length / 2
        self.trace_signal.n_right_secondary_counter = 1  # clicked once
        self.assertTrue(self.trace_signal.step_right_left(0, 0) == self.trace_signal.time_track[-1] -
                        self.trace_signal.window_length)

    def test_left_move(self):
        local_window_length = 3000
        self.trace_signal.window_length = local_window_length
        self.trace_signal.position = self.trace_signal.time_track[0] + 3 * self.trace_signal.window_length
        self.trace_signal.n_left_secondary_counter = 1
        self.assertTrue(self.trace_signal.step_right_left(0, 0) ==
                        self.trace_signal.time_track[0] + 2 * self.trace_signal.window_length)

    def test_beginning_left_move(self):
        """
        testing if the move to the left if position < window_length results in setting position to 0
        """
        local_window_length = 3000
        self.trace_signal.window_length = local_window_length
        self.trace_signal.position = self.trace_signal.time_track[0] + (self.trace_signal.window_length / 2)
        self.trace_signal.n_left_secondary_counter = 1
        self.assertTrue(self.trace_signal.step_right_left(0, 0) == self.trace_signal.time_track[0])


if __name__ == '__main__':
    unittest.main()