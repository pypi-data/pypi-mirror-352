﻿#-------------------------------------------------------------------------------
# Name:        AND
# Author:      Dhiabi Fathi
# Created:     14/03/2022
# Update:      01/04/2025
# Copyright:   (c) PyAMS
# Licence:     free
#-------------------------------------------------------------------------------

from pyams.lib import model, signal, param
from pyams.lib import voltage

# CMOS AND Gate Model ---------------------------------------------------------
class CAND(model):
    """
    This class models a **CMOS AND Gate**.

    The gate follows digital logic behavior:
    - If either input is **LOW (≤ IL)**, the output is **LOW (OL)**.
    - If both inputs are **HIGH (≥ IH)**, the output is **HIGH (OH)**.
    - Intermediate voltages are not handled explicitly in this model.

    :red:`Attributes`
    -----------------
    - **Vin1 (signal):** First input voltage
    - **Vin2 (signal):** Second input voltage
    - **Vout (signal):** Output voltage

    - **IL (param):** Input LOW voltage threshold (default = 0.2V)
    - **IH (param):** Input HIGH voltage threshold (default = 3.2V)
    - **OL (param):** Output LOW voltage (default = 0.0V)
    - **OH (param):** Output HIGH voltage (default = 5.0V)

    :red:`Methods`
    --------------
    - **analog():** Defines the AND gate behavior.

    :red:`Logic Table`
    ------------------
    | Vin1 | Vin2 | Vout |
    |------|------|------|
    |  LOW |  LOW |  LOW |
    |  LOW | HIGH |  LOW |
    | HIGH |  LOW |  LOW |
    | HIGH | HIGH | HIGH |

    """

    def __init__(self, Out, In1, In2):
        # Signal declarations --------------------------------------------------
        self.Vin1 = signal('in', voltage, In1)
        self.Vin2 = signal('in', voltage, In2)
        self.Vout = signal('out', voltage, Out)

        # Parameter declarations -----------------------------------------------
        self.IL = param(0.2, 'V', 'Input LOW voltage threshold')
        self.IH = param(3.2, 'V', 'Input HIGH voltage threshold')
        self.OL = param(0.0, 'V', 'Output LOW voltage')
        self.OH = param(5.0, 'V', 'Output HIGH voltage')

    def analog(self):
        """Defines the AND gate behavior using voltage threshold logic."""
        if (self.Vin1 <= self.IL) or (self.Vin2 <= self.IL):
            self.Vout += self.OL  # Output LOW if either input is LOW
        elif (self.Vin1 >= self.IH) and (self.Vin2 >= self.IH):
            self.Vout += self.OH  # Output HIGH if both inputs are HIGH
