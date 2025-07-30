"""
"""

# (1): Import the specialized `dataclass` library:
from dataclasses import dataclass

@dataclass
class CFFInputs:
    
    # (X): ...
    compton_form_factor_h: complex

    # (X): ...
    compton_form_factor_h_tilde: complex

    # (X): ...
    compton_form_factor_e: complex

    # (X): ...
    compton_form_factor_e_tilde: complex