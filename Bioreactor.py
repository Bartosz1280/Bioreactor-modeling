import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt
import math
#from MBequations import *
class SimulationInput:
    def __init__(self,inputs=None,**kwargs):
        if not inputs:
    
            const_list=[
                    'Y_xs','K_d','mu_max', 'K_i', "m",  "n", "K_s", "X_m", "S_m","K_1","K_2"
                    ]
    
            var_list = [
                    "X","S","P"
                    ]
            equations_specification = ['growth_type', 'biomass_eq_type','substrate_eq_type']
            self.constants =  {key: 
                            (dict(kwargs.items())[key] if key in dict(kwargs.items()) else None)
                            for key in const_list
                            }
    
            self.variables =  {key: 
                                (dict(kwargs.items())[key] if key in dict(kwargs.items()) else None)
                                for key in var_list
                                }
            
            self.equations_specification =  {key: 
                                (dict(kwargs.items())[key] if key in dict(kwargs.items()) else None)
                                for key in equations_specification
                                }
        else:
            self.constants, self.variables, self.equations_specification = inputs

    def get_inputs(self):
        return (self.constants, self.variables, self.equations_specification)
    def copy(self):
        return SimulationInput(inputs = self.get_inputs())


class SimpleBioreactor:

    def __init__(self,  time_arr, simulation_input, name="Bioreactor"):

        # Defining functions run on init

        # Initiation of constants and variables
        def init_constants(input_dict):
            for key in input_dict:
                if input_dict[key]:
                    setattr(self, key,  self.model.Const(value=input_dict[key],name=key))

        def init_variables(input_dict):
            for key in input_dict:
                if input_dict[key]:
                    setattr(self, key, self.model.Var(value=input_dict[key], lb=0 ,name=key))
                    #self.model.Equation(eval(f"self.{key}") >=0)

        # Initization of equations
        def add_biomass_eq (self):
            equation_type = self.equations_specification['biomass_eq_type']
            if not equation_type :
                equation_type = "biomass_growth_with_decay"
                self.equations_specification['biomass_eq_type'] = equation_type

            match equation_type.lower():
                case 'biomass_growth_with_decay':
                    self.dXdt = self.model.Intermediate(self.mu * self.X - self.K_d)
                case _:
                    raise KeyError("!!!")

        def add_substrate_eq (self):
            equation_type = self.equations_specification['substrate_eq_type']
            if not equation_type :
                equation_type = "reciprocal_decay"
                self.equations_specification['substrate_eq_type'] =equation_type
            
            match equation_type.lower():
                case 'reciprocal_decay':
                    self.dSdt = self.model.Intermediate((-1/self.Y_xs) *self.mu * self.X)
                case _:
                    raise KeyError("!!!")

        def add_growth_eq(self):

            equation_type = self.equations_specification['growth_type']

            if not equation_type :
                equation_type = "monod_substrate"
                self.equations_specification['growth_type'] = equation_type

            match equation_type.lower():

                case "monod_substrate":
                    self.mu = self.model.Intermediate(
                            ((self.mu_max * self.S) / (self.K_s + self.S))
                            )
                case "monod_substrate_biomass":
                    self.mu = self.model.Intermediate(
                            ((self.mu_max * self.S * self.X) / (self.K_s + self.S))
                            )
                case "blackman":
                    self.mu = self.model.Intermediate(
                            ((self.mu_max * self.S)/self.K_s)
                            )
                case 'tesseir':
                    self.mu = self.model.Intermediate(
                            self.mu_max*(1- math.e**(self.K_i*self.S))
                            )
                case "moser":
                    self.mu = self.model.Intermediate(
                            (self.mu_max * self.S ** self.n)/(self.K_s + self.S**self.n)
                            )
                case "webb":
                    self.mu = self.model.Intermediate(
                            (self.mu_max*self.S*(1+(self.S/self.K_i)))/
                            (self.S+self.K_s+(self.S**2/self.K_i))
                            )
                case 'haldane':
                    self.mu = self.model.Intermediate(
                            (self.mu_max * self.S)/(self.K_s + self.S+(self.S**2/self.K_i))
                            )
                case "contois":
                    self.mu = self.model.Intermediate(
                            (self.mu_max * self.S)/(self.K_s*self.X + self.S))
                case "aiba":
                    self.mu = self.model.Intermediate(
                            self.mu_max*(self.S/(self.K_s + self.S) * math.exp(-(self.S/self.K_i)))
                            )
                case 'han':
                    self.mu = self.model.Intermediate(
                            self.mu_max*(1-(self.S/self.S_m)**self.n*
                                        (self.S/(self.S + self.K_s*(1-self.S/self.S_m)**self.m )))
                            )
                case "powell":
                    self.mu = self.model.Intermediate(
                            ((self.mu_max + self.m)*self.S)/(self.K_s + self.S) - self.m
                            )
                case "verhulst":
                    self.mu = self.model.Intermediate(
                            self.mu_max*(1-(self.X/self.X_m))
                            )
                case 'luong':
                    self.mu = self.model.Intermediate(
                            self.mu_max*(self.S/(self.K_s+self.S)*(1-(self.S/ self.S_m)**self.n))
                            )
                case 'yano':
                    self.mu = self.model.Intermediate(
                            self.mu_max/(self.K_s+self.S+(self.S**2/self.K_1)+(self.S**2/self.K_2**2))
                            )
                case _:
                    raise NotImplemented(f"{equation_type} is not implemented")

        ### GEKKO model
        self.model = GEKKO(remote=False)
        self.model.time = time_arr
        ### Default options  
        self.model.options.IMODE = 4
        self.model.options.SOLVER = 1
        self.model.options.NODES = 3
        self.model.options.COLDSTART = 2

        self.id = name
        self.constants, self.variables, self.equations_specification = simulation_input
        
        self.mu = None
        self.dXdt = None
        self.dSdt= None
        self.dPdt = None

        init_constants(self.constants)
        init_variables(self.variables)
        add_growth_eq(self)
        add_biomass_eq(self)
        add_substrate_eq(self)

        self.model.Equation(self.S.dt() == self.dSdt)
        self.model.Equation(self.X.dt() == self.dXdt)

        # Biomass maximization
        self.model.Obj(-self.X)


    def add_constant(self, name: str, value):
        setattr(self, name, self.model.Const(value=value,name=name))

    def solve(self):
        self.model.solve(display=False)


    def plot(self):
       
        def latex_convert(name):
            name = name.split("_")
            # m or n 
            if len(name) == 1:
                name = f"$name$"
            # beta
            elif name[0] == name[0].lower() and len(name) == 1:
                name = f"$\\{name[0]}$"
            elif name[0] == "t":
                name = "$"+name[0] +"_{" + name[1] + "}$"
            # mu_max
            elif name[0] == name[0].lower() and len(name) > 1:
                name = "$\\"+name[0] +"_{" + name[1] + "}$"
            # K_i , Y_xs etc
            elif name[0] == name[0].upper() and len(name)  > 1:
                    name = f"${name[0]}" + "_{"+name[1]+"}$"
            return name

        def create_constants_box(y,x=0.005):
            
            text_to_plot = ["Constants"]

            for key  in list(filter(
                lambda key: self.constants[key] != None, self.constants
                )):
                if self.constants[key]:
                    text_to_plot.append(latex_convert(key) +": "+ str(self.constants[key]))
            text_to_plot = "\n".join(text_to_plot)
            return ax.text(
                x , y, 
                text_to_plot,
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes, fontsize=8,
                bbox={'facecolor': 'orange', 'alpha': 0.45, 'pad': 5}
             )

        def create_eq_types_box(y,x=0.01):
            text_to_plot = "\n".join(
                    [ key.split("_")[0]+": "+self.equations_specification[key]
                     for key in self.equations_specification])
            return ax.text(
                x , y, 
                text_to_plot,
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes, fontsize=8,
                bbox={'facecolor': 'blue', 'alpha': 0.45, 'pad': 5}
             )

        def create_variables_box(self,y,x=0.175):
            def get_ranges(self, key):
                return (
                        "{:.2e}".format(max(eval("self."+str(key)))),
                        "{:.2e}".format(min(eval("self."+str(key))))
                        )
            def create_ranges_str(key):
                return (f"{latex_convert(key+'_max')}: {variables[key][0]}\n{latex_convert(key+'_min')}: {variables[key][1]}")

            keys = list(filter(lambda x: self.variables[x] != None, self.variables))
            variables = {key:get_ranges(self, key) for key in keys}
            variables = [create_ranges_str(key) for key in variables]
            variables.insert(0,"Variables:")
            text_to_plot = "\n".join(variables)
            return ax.text(
                x , y, 
                text_to_plot,
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes, fontsize=8,
                bbox={'facecolor': 'red', 'alpha': 0.45, 'pad': 5}
             )
            
        fig = plt.figure()
        ax = fig.add_subplot()
        fig.suptitle(f'{self.id} plot', fontsize=14, fontweight='bold')
        ax.set_title(f'{len(self.model.time)} sample for {latex_convert("t_max")}={int(max(self.model.time))} h')
        ax.plot(self.model.time, self.S.value,label='S - subtrate')
        ax.plot(self.model.time, self.X.value,label='X - biomass')
     
        create_constants_box(y=-0.5)
        create_eq_types_box(y=-0.25)
        create_variables_box(self,y=-0.5)

        ax.set_xlabel('time [h]')
        ax.set_ylabel('(dS/dX)dt')
        
        ax.legend()
        ax.grid()
        return(ax)
