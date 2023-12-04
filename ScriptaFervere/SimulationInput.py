# HEAD :  Class SimulationInput
#
# Class for easy creation of input for Bioreactor
# by class declatation
#
#
# TODO : Checking var/const vs equations coherence
# TODO : Drop equation to secrect attribute and and make a function for displaying 
# equations of the model



class SimulationInput:
    """
    Class SimulationInput (inputs=None, **kwargs)

    Is the class for creating, handling and outputing parameters used by
    different optimization models. Each kwargs should be a name of contant
    or variable, or equation(passed as string). An instance will hold a
    multiple basics variables and constans assigned by default to zero, when no
    **kwargs are passed. After being initialized an instansce holds most data as
    dictionaries bounded to its attributes. 
    An instnace can be initialized as well by passing input tuple to inputs parameter.
    This method is meant to fast and easy declearing of new instnaces with the same 
    attrbitues for creating multiple scenarioes without writing all inputs again.

    The instnace contains three main attributes which are of dictionary type:
          - SimulationInput.constants - contains constans to be intepreted as GEKKO.Const
          - SimulationInput.variables - contains variables to be intepreted as GEKKO.Var
          - SimulationInput.equations -  contains equations to be intepreted as GEKKO.Intermediate. Keys of
          that dictionary unlike previous two contains tuples with two strings representing the same equation.
          The first representation is a human redable version of the equation, whereas the second is the same 
          equation createad as an expression that can intepreted by python as an operation on instances attrbitues.

    Methods:
        - SimulationInput.get_inputs() - return a tuple that is unpacked by instance of SimpleBioreactor
        - SimulationInput.copy() - reaturn an instance of SimulationInput containing the same attrbitues as 
        the instance in which the method was called.
        - SimulationInput.add_equation(equation) - allows to adding a new equation after instance declaration
        in a way that can be intepreted by SimpleBioreactor as part of an input tuple.
        - SimulationInput.__str__()
    """

    def __init__(self,inputs=None,**kwargs):
        # Functions used for proper handling of equations
        # When kwargs are passed an instance fill atrributues with some general
        # variables and constants assigned to None, unless specified.
        # Setting parameter to None instead of zero is required for predictable and
        # fast validation of a GEKKO model. Later on  each parameter can  be manually
        # changed by altering attrbitues (dictionaries)

        self.growth_models_pallet = {
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
                    "mu", "dXdt", "dSdt"
                    ]
            
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
                # Detects initial value of a variable
                if "_0" in key:
                    self.variables[key] = value
                # Detects if pre-build growth model is requested
                elif key.lower() in ["growth_type", "growth" , "growth_model"]:
                    self.equations["mu"] = self.growth_models_pallet[value]
                # Detects if contians is requested
                elif "_" in key:
                    self.constants[key] = value
                # Detects if an equation is passed
                elif key == key.upper() or "dt" in key:
                    self.equations[key] = value

            # Now equations shall be translated into a python compatible string
            for key, value in self.equations.items(): # REFRACTION NEEDED
                # Some variable/constans might be not defined at init
                # leading them to be None. This will rise and AttributeError
                # at next step, thus try/except expression was set to avoid it.
                # Nevertheless this might be change during later stages of development
                # to force passing a defined minimal input to run a model, thus 
                # checking inputs a step before passing them to the model.
                try:
                    spaced_equation = self._fix_spacing(value)
                    python_equation = self._cast_equation_to_python_str(spaced_equation)
                    # To retain more human redable version both equations
                    # are passed to a tuple which becomes a new value for a key
                    self.equations[key] = (spaced_equation, python_equation)
                except AttributeError:
                    self.equations[key] = (None, None)

        # Passing defined inputs parameter is predominatlly used to copy
        # simulation inputs, thus this method of initialization is not
        # meant for ad hoc instance declation.
        else:
            self.constants, self.variables, self.equations_specification = inputs

# End of __init__

    def __str__(self):

        def get_number_of_defined_keys(atr_dict):
            """
            Returns a tuple of var/const, where ind 0 gives a number
            of all keys within a dictionary and ind 1 a number of valeus
            that are not None
            """
            all_keys = len(atr_dict)
            defined_keys = len(list(filter(lambda x : x != None and x != (None, None), atr_dict.values())))
            return(all_keys, defined_keys)

        def start_new_section(label: str, text: list):
            "Alias function for creating heading for new sections"
            text.append(f'\n{label}')
            text.append("=========================")

        number_of_defined_const = get_number_of_defined_keys(self.constants)
        number_of_defined_variables = get_number_of_defined_keys(self.variables)
        number_of_defined_equations = get_number_of_defined_keys(self.equations)
        
        # Unspecified var/conts/equat will be passed to a corresponding list
        # Next these list will be used for outputing information about not
        # definined attributes.

        unspec_const, unspec_var  =  list() , list()

        # The outputed text is stored in text: list variable. Additional lines are appended to 
        # the text variable. Their number and, form and contnet are dependent on kwargs
        # specified on instance initialization
        text = [
            "SimulationInput instance ",
            "=========================",
            # Fast check allowing how many variables, contains and equations are declated
            # and how many of them are specified
            f"{number_of_defined_const[0]} constants, with {number_of_defined_const[1]} defined.",
            f"{number_of_defined_variables[0]} variables, with {number_of_defined_variables[1]} defined.",
            f"{number_of_defined_equations[0]} equations, with {number_of_defined_equations[1]} defined.",
        ]

        start_new_section("Variables at t_0", text)

        for key, value in self.variables.items():
            if value:
                text.append(f" {key} = {value}")
            else: 
                unspec_var.append(key)

        start_new_section("Equations", text)

        # Appending equations to the text variable.
        #
        # Human redable version of an equation is retrived from tuples (index 0)

        for dependent_var, equations_tuple in self.equations.items():
            if equations_tuple != (None,None):
                equation = equations_tuple[0]
                text.append(f" {dependent_var} = {equation}")
            else:
                text.append(f" {dependent_var}  is Undefined!")
        start_new_section("Constans",text)

        # Appending of constants to the text variable

        for key, value in self.constants.items():
            if value:
                text.append(f" {key} = {value}")
            else:
                unspec_const.append(key)

        if unspec_const != list():
            start_new_section("Not specified constants", text)
            text.append(" ;".join(unspec_const))

        if unspec_var != list():
            start_new_section("Not specified variables", text)
            text.append(" ;".join(unspec_var))

        return "\n".join(text)

# Class methods
    def change_growth_model(self, growth_model: str):
        """
        SimulationInput.change_growth_model(growth_model: str)

            Method allows to change a growth model without defing a full 
        equation, but calling it by a tag string. This call is mapped to
        a pre-build growth models within a SimulationInput.growth_models_pallet
        attribute. The function ensures that the euqation is passed correctly.

        If desired model is not included in the attribute, it can be passed like
        a regular equation using SimulationInput.add_equation() method.
        """

        try:
            mu = self.growth_models_pallet[growth_model]
            equation = self._fix_spacing(mu)
            python_equation = self._cast_equation_to_python_str(equation)
            # To retain more human redable version both equations
            # are passed to a tuple which becomes a new value for a key
            self.equations['mu'] = (equation, python_equation)

        except KeyError:
            # Raises a KeyError but with more informative message
            raise KeyError(f"Requested {growth_model} is not implemented in pre-build models")

    def get_inputs(self):
        """
        SimulationInput.get_inputs()

            Method return a tuple with inputs for simulations.
        Such tuple can be direcly passed to Bioreactor instance for
        its initialization

        RETURN: tuple with simulations input
        """

        return (self.constants, self.variables, self.equations)

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

    def add_equation(self, equation: str):
        """
        SimulationInput.add_equation(equation: str)

        Method for parsing new equation after SimulationInput instance 
        is initialized. Unlike manual declation of a new key in equations
        attributes, using this function ensures that the equation will be 
        in a version compatible with SimpleBioreactor instance, by handling
        all equations string transformations.

        INPUT: equation: str - An equation to be added to the instance in form of string
        """
        class EquationError (Exception):
            "Custom exception to be raised if wrong equation is passed"
            def __init__(self, msg: str):
                self.message = msg
                super().__init__(self.message)

        # First the function will ensure that the input contians a full equation by
        # determing if the expresion contains = 
        if "=" not in equation:
            raise EquationError(
                f"Passed {equation} does not appears to be a full expresion. Ensure it contains = ")
        # In case an input contains multiple = , instead of rising ValueError a custim EquationError
        # is raised with most probable cause of an error.
        try:
            variable , expression = equation.split("=")
            # Removing empty spaces to overwrite a value instead of
            # setting a new key.
            variable = list(filter(lambda x : x != '', variable.split(" ")))[0]
        except ValueError:
            raise EquationError(f"{equation} appears to have multiple = " )
        # At the second stange function will ensure that  the passed equation has only one
        # varaible on its left side.
        if len(list(filter(lambda x: x != "", variable.split(" "))))  > 1:
            raise EquationError(f"Passed {equation} appears to describe multiple dependent variables.")

        equation = self._fix_spacing(expression)
        python_equation = self._cast_equation_to_python_str(equation)
        # To retain more human redable version both equations
        # are passed to a tuple which becomes a new value for a key
        self.equations[variable] = (equation, python_equation)
        print(f"> {variable} = {equation} was added")
        
# Secret functions

    def _fix_spacing(self, equation: str):
        """
        Hidden function - Previously a sub-function of __init__ 

        Fixes not coherent spacing in passed equation and translat
        some popular mathematical operations formating to version
        correct with python syntax.

        Function should be used on an input before it is passed to 
        _cast_equation_to_python_str function to ensure that function
        will correctly rewrite the expression.

        INPUT: equation: str - string containg a mathematical equation
        OUTPUT: equation string that is evenly spaced, thus will be 
        correctly processed bu _cast_equation_to_python_str function
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

    def _cast_equation_to_python_str(self, equation: str):
        """
        Hidden function - Previously a sub-function of __init__

        This function transforms a human redable equation string to
        one that can be intepreted by python with its math library.

        Befor applying this function on any equation string an input
        should be processed by _fix_spacing function for stable and 
        intended string manipulation.
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

