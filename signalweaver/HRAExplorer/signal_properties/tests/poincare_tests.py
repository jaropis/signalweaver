import unittest
from numpy import round
from signal_properties.RRclasses import Signal


class TestPoincare(unittest.TestCase):

    def setUp(self):
        self.signal_real1 = Signal("RR1.csv", 1, 2, annotation_filter=(2,))
        self.signal_real1.set_poincare()

    def test_first_signal_SD1(self):
        self.assertTrue(round(self.signal_real1.poincare.SD1, 3) == 36.807)  # this is an example from our tutorial
        # uncomment the line below and comment the line above if you want to use the definition of variance which uses (n-1)
        # self.assertTrue(round(self.signal_real1.poincare.SD1, 3) == 36.817)  # this is an example from our tutorial

    def test_first_signal_SD2(self):
        self.assertTrue(round(self.signal_real1.poincare.SD2, 3) == 86.253)  # this is an example from our tutorial
        # uncomment the line below and comment the line above if you want to use the definition of variance which uses (n-1)
        #self.assertTrue(round(self.signal_real1.poincare.SD2, 3) == 86.275)  # this is an example from our tutorial

    def test_first_signal_SDNN(self):
        self.assertTrue(round(self.signal_real1.poincare.SDNN, 3) == 66.311)  # this is an example from our tutorial
        # uncomment the line below and comment the line above if you want to use the definition of variance which uses (n-1)
        #self.assertTrue(round(self.signal_real1.poincare.SDNN, 3) == 66.328)  # this is an example from our tutorial

    def test_short_term_asymmetry(self):
        self.assertTrue(round(self.signal_real1.poincare.SD1d, 3) == 26.418)
        self.assertTrue(round(self.signal_real1.poincare.C1d, 2) == 0.52)
        self.assertTrue(round(self.signal_real1.poincare.SD1a, 3) == 25.630)
        self.assertTrue(round(self.signal_real1.poincare.C1a, 2) == 0.48)

    def test_long_term_asymmetry(self):
        self.assertTrue(round(self.signal_real1.poincare.SD2d, 2) == 59.36)
        self.assertTrue(round(self.signal_real1.poincare.C2d, 2) == 0.47)
        self.assertTrue(round(self.signal_real1.poincare.SD2a, 2) == 62.58)
        self.assertTrue(round(self.signal_real1.poincare.C2a, 2) == 0.53)

    def test_total_asymmetry(self):
        self.assertTrue(round(self.signal_real1.poincare.SDNNd, 2) == 45.94)
        self.assertTrue(round(self.signal_real1.poincare.Cd, 2) == 0.48)
        self.assertTrue(round(self.signal_real1.poincare.SDNNa, 2) == 47.81)
        self.assertTrue(round(self.signal_real1.poincare.Ca, 2) == 0.52)

if __name__ == '__main__':
    unittest.main()
