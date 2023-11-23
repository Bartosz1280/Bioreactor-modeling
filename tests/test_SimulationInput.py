# HEAD test_SimulationInput.py
#
# File for testing SimulationInput class with its 
# functionalities.c

import pytest
import os
from ScriptaFervere.SimulationInput import SimulationInput


def simple_initiation_test():
    """
    The following test aim to asses if paraments passed as **kwargs are correctly
    distributed among attributes (that are dicrionaries). Except for that functions
    for converting equations 
    """
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

    assert test_SimulationInput.constants == {
            'Y_xs': 1.28, 'K_d': 0.0033,'mu_max': 0.86,
            'K_i': None, 'm': None, 'n': None,
            'K_s': 0.0138, 'X_m': None, 'S_m': None,
            'K_1': None, 'K_2': None}
    assert test_SimulationInput.variables == {
            'X_0': 0.005, 'S_0': 0.07}
    assert test_SimulationInput.equations == {
        'mu': 
        (
            ' ( mu_max * S )  /  ( K_s + S ) ',
            '(self.mu_max*self.S)/(self.K_s+self.S)'
            ),
        'dXdt': (
            'mu * X - K_d', 
            'self.mu*self.X-self.K_d'
            ),
        'dSdt': (
            ' - 1 / Y_xs * mu * X',
            '-1/self.Y_xs*self.mu*self.X')
        }


def growth_models_initation_tests():
    """
    Following test aims to evaluate if builfd-in growth models are passed correctly to
    the instance of SimulationInput.
    """
    models =  { 
        "monod_substrate" : "(mu_max * S) / (K_s + S)",
        "monod_substra_biomass" : "(mu_max * S * X) / (K_s +S)",
        "blackman" :"( mu_max * S ) / K_s",
        "tesseir" :"mu_max * e **( K_i ) * S",
        "moser" : "( mu_max * S ** n )/( K_s + S ** n )",
        "webb" : "( mu_max * S *( 1 + ( S / K_i ))) /( S + K_s + ( S ** 2/ K_i ))",
        "haldane" : "( mu_max * S)/( K_s + S + ( S**2 / K_i ))",
        "contois" : "( mu_max * S ) / ( K_s * X + S )",
        "aiba" : "( mu_max * ( 1- ( S / S_m ) ** n * ( S / ( S + K_s * (1 - S / S_m) ** m ))))",
        "powell" : "(( mu_max + m ) * S ) / ( K_s + S) - m",
        "verhulst" : "mu_max * ( 1 - ( X / X_m ))",
        "luong" : "mu_max *  ( S / ( K_s + S ) * (1 -(S / S_m) ** n))",
        "yano" : "mu_max / ( K_s + S + ( S ** 2 / K_1) + ( S ** 2/ K_2 ** 2))"
    }

    for key, value in models.items():
       test_instance = SimulationInput(growth = key)
       assert test_instance.equations['mu'][0] == value
       print(f"model {key} passed")

if __name__ == "__main__":
    simple_initiation_test()
    growth_models_initation_tests()
