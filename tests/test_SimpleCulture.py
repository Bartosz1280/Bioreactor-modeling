import pytest
import os
import numpy as np

import ScriptaFervere
from ScriptaFervere.SimulationInput import SimulationInput
from ScriptaFervere.Models import SimpleCulture

test_SimulationInput = SimulationInput(
            mu_max = 0.86, 
                       K_s = 0.0138,
                       Y_xs = 1.28,
                       K_d = 3.3e-3, 
                       X_0 = 0.005,
                       S_0 = 0.07,
                       growth= "monod_substrate",
                       dSdt ="-1/Y_xs * mu * X",
                       dXdt="mu * X - K_d")

inputs = test_SimulationInput.get_inputs()
time_arr = np.linspace(0,15,1000)
test_model = SimpleCulture(time_arr, inputs)
