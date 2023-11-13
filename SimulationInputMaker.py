# HEAD :  Class SimulationInputMaker
#
# Class for easy creation of input for Bioreactor
# by class declatation
#
# TODO : Implement functions for handling equations 
# from string.



class SimulationInput:
    """
    Class SimulationInput (**kwargs)

    Is the class for creating, handling and outputing parameters used by
    different optimization models. Each kwargs should be a name of contant
    or variable, or equation(passed as string). An instance will hold a
    multiple basics variables and constans assigned by default to zero, when no
    **kwargs are passed. After being initialized an instansce holds most data as dictionaries bounded
    to its attributes.
    """

    def __init__(self,inputs=None,**kwargs):
        # Functions used for proper handling of equations
        def fix_spacing(equation: str):
            """
            Sometimes an equation might be pased with not coherent spacing, hindering proper str
            to equation conversion. To avoid these problems and make the code
            simpler be defualt each equations is passed into that function.

            Except for that using that function returns an equation in human redable string.
            """
            universal_math_operators = [
                   "+" , "-" , "*","**",
                   "/",  "(" , ")" , "[","]"]
            equation = "".join(equation.split(" "))
            # Makes sure that power will not be mistook for multiplication
            equation = " ^ ".join(equation.split("**"))
            # First loop takes care of correct spacing for universal operators
            for i in universal_math_operators: # MIGHT REQUIRE SOME DEBUGGING !
                equation = f" {i} ".join(equation.split(i))
            equation = "**".join(equation.split("^"))
            
            return equation

        def cast_equation_to_python_str(equation: str):
            """
            This function transforms a human redable equation string to
            one that can be intepreted by python.
            """
            universal_math_operators = [
                   "+" , "-" , "*","**",
                   "/",  "(" , ")" , "[","]"]
            # Using additonal list shall allows easier passing of the formula by 
            # using some popular notation that is not recogniazable by python.
            popular_math_operators=["^", "ln","log", "exp"]
            # Its vital to pass correctly spaced formula for the function, 
            # since it itterates through a list not a string.
            equation_list = equation.split(" ")
            for i in equation_list:
                try:
                    float(i)
                    # If false tries to determine if i is var/conts 
                    # or mathematical operation
                except ValueError:
                        # Grabs mathematical operation to convert it 
                        # to python redable expression
                    if i in popular_math_operators:
                        match i:
                            case "^":
                                equation_list[equation_list.index(i)] = "**"
                            case "ln":
                                equation_list[equation_list.index(i)] = "math.ln"
                            case "log":
                                equation_list[equation_list.index(i)] = "math.log"
                            case "exp":
                                equation_list[equation_list.index(i)] = "math.exp"
                    # Remainig possiblity is that i is var/const
                    elif i not in universal_math_operators and i !="":
                        equation_list[equation_list.index(i)] = f"self.{i}"

            return "".join(equation_list)

        # When kwargs are passed an instance fill atrributues with some general
        # variables and constants assigned to None, unless specified.
        # Setting parameter to None instead of zero is required for predictable and
        # fast validation of a GEKKO model. Later on  each parameter can  be manually
        # changed by altering attrbitues (dictionaries)
        if not inputs:
            # This list defines constans that have a defined value and are treated as 
            # GEKKO Constans within the Bioreactor instance.
            const_list=[
                    'Y_xs','K_d','mu_max', 'K_i', "m",  "n", "K_s", "X_m", "S_m","K_1","K_2"
                    ]
            # This list defines initial values of variables at t=0
            var_list = [
                    "X_0","S_0","P_0"
                    ]
            # This list defines formulas needed for a minimal model
            equations = [
                    "mu", "X", "S"
                    ]

            #equations_specification = ['growth_type', 'biomass_eq_type','substrate_eq_type']

            self.constants =  {key: 
                            (dict(kwargs.items())[key] if key in dict(kwargs.items()) else None)
                            for key in const_list
                            }
            self.variables =  {key: 
                                (dict(kwargs.items())[key] if key in dict(kwargs.items()) else None)
                                for key in var_list
                                }
            self.equations =  {key: 
                                (dict(kwargs.items())[key] if key in dict(kwargs.items()) else None)
                                for key in equations
                                }

            # Loop below grabs remaining var/con/equation that are not
            # specified within the class. It's important to follow 
            # the convention on naming var/con/equations for the 
            # correct assigment
            for key, value in kwargs.items():
                if "_0" in key:
                    self.variables[key] = value
                elif "_" in key:
                    self.constants[key] = value
                elif key == key.upper():
                    self.equations[key] = value

            # Now equations shall be translated into a python compatible string
            for key in self.equations:
                equation = self.equations[key]
                spaced_equation = fix_spacing(equation)
                python_equation = cast_equation_to_python_str(spaced_equation)
                # To retain more human redable version both equations
                # are passed to a tuple which becomes a new value for a key
                self.equations[key] = (spaced_equation, python_equation)

        # Passing defined inputs parameter is predominatlly used to copy
        # simulation inputs, thus this method of initialization is not
        # meant for ad hoc instance declation.
        else:
            self.constants, self.variables, self.equations_specification = inputs

    def __str__(self):
        text = [
            head := "SimulationInput instance \n",
            spacer := "============\n",
            subhead := f"Initialized with {len(self.constants)} constants, {len(self.variables)} variables, {len(self.equations)} equations \n",
            const_list := [f"{key} {self.constants[key]} \n" for key in self.constants],
            variables_list := [f"{key} {self.variables[key]} \n" for key in self.variables],
            equations_list := [f"{key} {self.equations[key]} \n" for key in self.equations],
        ]
        return text


    def get_inputs(self):
        """
        SimulationInput.get_inputs()

            Method return a tuple with inputs for simulations.
        Such tuple can be direcly passed to Bioreactor instance for
        its initialization

        RETURN: tuple with simulations input
        """

        return (self.constants, self.variables, self.equations_specification)

    def copy(self):
        """
        SimulationInput.copy()

            Method that returns a new instance of SimulationInput 
        for already exsiting instance. This aims to shorten time
        needed for drawing multiple simulation scenarious, where only
        one or a few parameters differs.
            Newly create instance can be altered just by switching some values in
        dictionaires stored as attributes.

        RETURN :: SimulationInput instance with copied attributes
        """

        return SimulationInput(inputs = self.get_inputs())


