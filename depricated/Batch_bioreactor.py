# HEAD
#
# This is the first implementation of model in OOP way that is left to
# help during new implementations, and will not be avaible in the final release


from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

class Batch_bioreactor:
    """
    Class Batch_bioreactor

    Integrates variables and constants  describing batch bioreactor performance
    into a GEKKO model, and handles inputs and outputs of the model

    Arguments:
        time_arr: iterrable - array of timepoints for ODE input
        parameters: dict - containing values that do not change overtime
        variables: dict - contains all variables that change overtime

    """
    def __init__(self, time_arr, parameters: dict, variables: dict):
        
        ### GEKKO model
        self.model = GEKKO(remote=False)
        self.model.time = time_arr
        ### Default options  
        self.model.options.IMODE = 4

        self.model.options.SOLVER = 1
        self.model.options.NODES = 3
        self.model.options.COLDSTART = 2
        
        ### Constants
        
        # Maximal growth rate
        self.mu_max = self.model.Const(value=parameters["mu_max"], name="mu_max")
        # 
        self.K_s = self.model.Const(value=parameters["K_s"], name="K_s")
        #
        self.Y_xs = self.model.Const(value=parameters["Y_xs"], name="Y_xs")
        #
        self.K_d = self.model.Const(value=parameters["K_d"], name="K_d")
        
        ### Variables
        self.X = self.model.Var(value=variables["X_0"], name="X_0")
        self.S = self.model.Var(value=variables["S_0"], name="S_0")
        
        ### Intermediate equation
       
        # Specific growth rate
        self.mu = self.model.Intermediate(self.mu_max * (self.S / (self.K_s + self.S)))
        # Change in substrate concentration overtime
        self.dSdt = self.model.Intermediate(-1/self.Y_xs * self.mu * self.X)
        # Change in biomass overtime
        self.dXdt = self.model.Intermediate(self.mu * self.X - self.K_d)
        
        # Equation
        self.model.Equation(self.S.dt() == self.dSdt)
        self.model.Equation(self.X.dt() == self.dXdt)

        # Biomass maximization
        self.model.Obj(-self.X)

    def solve(self):
        self.model.solve(display=False)
        
    def plot(self):
        
        def text_value(latex, value,y, x =0.005):
             return ax.text(
                x , y, 
                f'{latex}: {value}',
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes, fontsize=8,
                bbox={'facecolor': 'orange', 'alpha': 0.5, 'pad': 0}
             )
            
        def text_header(text,y, x =0.005):
             return ax.text(
                x , y, 
                text,
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes, fontsize=10, style='oblique',
                bbox={'facecolor': 'orange', 'alpha': 0.5, 'pad': 1}
             )
            
        fig = plt.figure()
        ax = fig.add_subplot()
        fig.suptitle('Change of Batch-bioreactor overtime', fontsize=14, fontweight='bold')
        ax.set_title(f'$t_n$={len(self.model.time)}')
        ax.plot(self.model.time, self.S.value,label='S - subtrate')
        ax.plot(self.model.time, self.X.value,label='X - biomass')
        text_value('$\mu_{max}$', self.mu_max.value, y=0.05)
        text_value('$K_{s}$', self.K_s.value, y = 0.10)
        text_value('$Y_{xs}$', self.Y_xs.value, y=0.15)
        text_value('$K_{d}$', self.K_d.value, y=0.20)
        text_header('Constants:', y=0.25)
        ax.set_xlabel('time [h]')
        ax.set_ylabel('(dS/dX)dt')

        
        ax.legend()
        ax.grid()
