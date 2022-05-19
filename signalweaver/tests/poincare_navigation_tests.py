import unittest
from signalweaver.dash_files.dash_rep import DashECGSignal

import json


class TestPoincareClicks(unittest.TestCase):

    def setUp(self):
        name = '2017MEN_001rest.csv'
        self.dash_signal = DashECGSignal(name)

    def test_click_on_PP(self):
        # the json files contain "clicks" recorded while using signalwieaver
        # first loading first click on the poincare
        click_file = open('signalweaver/tests/json_click_data1.json', 'r')
        click_pp_1 = json.load(click_file)
        click_file.close()
        self.dash_signal.set_position_on_pp_click(click_pp_1)
        # now go to another position and click through
        click_file =open('signalweaver/tests/json_rr_click_norm_to_ven.json', 'r')
        click_rr_1 = json.load(click_file)
        click_file.close()
        # I will stop here - need to rewrite or learn selenium
        #self.dash_signal.