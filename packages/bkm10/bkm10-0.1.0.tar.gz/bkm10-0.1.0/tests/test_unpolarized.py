# tests/test_unpolarized.py

# (X): Native Library | unittest:
import unittest

# (X): External Library | NumPy:
import numpy as np

# (X): Self-Import | BKM10Inputs:
from bkm10_lib.inputs import BKM10Inputs

# (X): Self-Import | CFFInputs:
from bkm10_lib.cff_inputs import CFFInputs

# (X): Self-Import | DifferentialCrossSection
from bkm10_lib.core import DifferentialCrossSection


# (X): Define a class that inherits unittest's TestCase:
class TestUnpolarizedCoefficients(unittest.TestCase):

    def setUp(self):
        self.test_kinematics = BKM10Inputs(
            lab_kinematics_k = 5.75,
            squared_Q_momentum_transfer = 1.82,
            x_Bjorken = 0.34,
            squared_hadronic_momentum_transfer_t = -0.17)

        self.test_cff_inputs = CFFInputs(
            compton_form_factor_h = complex(-0.897, 2.421),
            compton_form_factor_h_tilde = complex(2.444, 1.131),
            compton_form_factor_e = complex(-0.541, 0.903),
            compton_form_factor_e_tilde = complex(2.207, 5.383))
        
        
