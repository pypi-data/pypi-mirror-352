"""
"""

# (1): Import the specialized `dataclass` library:
from dataclasses import dataclass

@dataclass
class BKM10Inputs:
    # (X): Q^{2}: photon virtuality:
    squared_Q_momentum_transfer: float

    # (X): x_{B}: Bjorken's x:
    x_Bjorken: float

    # (X): t: hadron momentum transfer: (p - p')^{2}:
    squared_hadronic_momentum_transfer_t: float

    # (X): ...
    lab_kinematics_k: float