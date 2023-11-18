# HEAD: Models.py
#
# File containing differnt models that interpreate SimulationInput to GEKKO
# Currently the simples model is included
#
# TODO Debug code, None variables are passed instead of being filtered out. It can be
# reproduced by adding P_0 variable to SimulationInput defaults without further specification
# TODO Comment code and write dockstrings



import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt
import math


class SimpleCulture:
    """
    Minimal model describing a culture biomass growth with a substrate constraint in
    a sigle batch mode.
    """
    def __init__(self,  time_arr, simulation_input, name="SimpleCulture"):

        # Defining functions run on init

        def init_constants(const_dict):
            "Sub function of __init__ used to asssignt constantsto attributes."
            for key , val in const_dict.items():
                # Not assigned constants are not pass to the model
                # to avoid uncessery declarations within the self.model
                if val:
                    setattr(self, key,  self.model.Const(value=val,name=key))

        def init_variables(variables_dict):
            "Sub function of __init__ for correct assgiment of variables to attributes"
            for key, val in variables_dict.items():
                if val:
                    variable_name = key.split("_0")[0]
                    setattr(
                            self, variable_name,
                            self.model.Var(
                                # Lower bound for a variable is set to zero to avoid
                                # unrealistic results like negative biomass at the end 
                                # of a simulation
                                value=variables_dict[key], lb=0 ,name=variable_name)
                            )

        def init_intermediates(equation_dict):
            "Sub function of __init__ for correct equations assgiment"
            for key, val in equation_dict.items():
                if val != (None, None): # BUG that pass undefined variables to the model
                    # values of equation_dict are tuple with human redable equation
                    # as the first value and python redable equation as second. 
                    # The second variant can be interpeted by GEKKO
                    python_equation = val[1]
                    setattr(self, key, self.model.Intermediate(eval(python_equation)))
                   
        def init_equations(variables_dict: dict, equation_dict: dict):
            "Sub function of __init__ used to define ODEs to be solved and binding them with previously initiated variables"

            class ErrorODE (Exception):
                "Custom exception to be raised when ODE cannot be mapped to defined variable"
                def __init__(self, msg: str):
                    self.message = msg
                    super().__init__(self.message)

            def ode_filter(var_name):
                """
                List made out of filter expression that maps an ODE to a passed variable
                """
                return list(filter(lambda x : var_name in x, ode_labels ))

            # First a list of keys that might be assosiated to ODE is created out of
            # all passed equations
            ode_labels = list(filter(lambda x : 'dt' in x.lower(),equation_dict.keys()))

            # In the next step variables are assosiated with detected ODEs

            for i in variables_dict.keys():
                # Variables that are in the dictionary decleared out of SimulationInput
                # presents with _0 index indicating that they represent and intial value.
                # In GEKKO models these variables present without that indexing to present
                # an array of value that is yeild from the simulation. In ODE labels they
                # present in dVardt notation where Var is the variable symbol.
                var_name = i.split("_0")[0]

                # In next step code ensures that exacly one ODE is mapped per variables
                if len(ode_filter(var_name)) == 0:
                    raise ErrorODE(f"Variable {var_name} cannot be assosiated with any ODE")
                elif len(ode_filter(var_name)) > 1:
                    raise ErrorODE(f"Variable {var_name} has multiple candiates for ODE")

                # When condition is met a python expression is declared and evaluated
                # in GEKKO.Equation()
                else:
                    eq_str = f"self.{var_name}.dt() == self.{ode_filter(var_name)[0]}"
                    self.model.Equation(eval(eq_str))

        ### GEKKO model
        self.model = GEKKO(remote=False)
        self.model.time = time_arr
        ### Default options  
        self.model.options.IMODE = 4
        self.model.options.SOLVER = 1
        self.model.options.NODES = 3
        self.model.options.COLDSTART = 2
        self.model.options.CSV_WRITE = 0 # Change it to 1 or 2 to get reesults in .csv file

        self.id = name
        self._solved = False

        # The prefered way of specifying inputs is by using SimulationInput
        # instance, thus to avoid manipulations on inputs within the SimpleCulture
        # all inputs are caseted to secret attributes.
        self._constants, self._variables, self._equations = simulation_input
        
        init_constants(self._constants)
        init_variables(self._variables)
        init_intermediates(self._equations)
        init_equations(self._variables, self._equations)


        # Biomass maximization
        self.model.Obj(-self.X)

    def solve(self):
        """
        Alias for SimpleCulture.model.solve(display=False)
        """
        self.model.solve(display=False)
        self.model.open_folder()
