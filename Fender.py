import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from scipy.interpolate import interp1d

class Fender():

    def __init__(self, depth, rated_energy, rated_reaction, energy_tolerance, reaction_tolerance) -> None:
        
        self.depth = depth
        self.rated_energy = rated_energy
        self.rated_reaction = rated_reaction
        self.energy_tolerance = energy_tolerance
        self.reaction_tolerance = reaction_tolerance
        self._fender_performance = None

        self._temperature_factor_table = np.array([
            [-30.0,-20.0,-10.0,0.000,10.00,23.00,30.00,40.00,50.00],
            [1.540,1.249,1.130,1.075,1.030,1.000,0.978,0.947,0.916]
        ]).transpose()
      
        self._velocity_factor_table = np.array([
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
            [1.20,1.16,1.14,1.13,1.11,1.10,1.09,1.09,1.08,1.07,1.07,1.06,1.06,1.05,1.05,1.05,1.04,1.04,1.04,1.03]
        ]).transpose()

    def __annotate_axes__(self, ax, title, x_axis, y_axis, xlim, ylim, reverse_x=False, reverse_y=False,fontsize=16):
        ax.set_label(title)
        ax.set_xlabel(x_axis)
        ax.set_ylabel(y_axis)
        #ax.get_legend().remove()
        ax.grid(True)
        ax.margins(0)
        ax.set_xlim([0,xlim])
        ax.set_ylim([0,ylim])
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        
        if reverse_y:
             ax.yaxis.tick_right()
             ax.yaxis.set_label_position("right")
        elif reverse_x:
            ax.xaxis.tick_top()
            ax.xaxis.set_label_positon("top")

        #ax.text(0.5, 0.5, text, transform=ax.transAxes,
        #ha="center", va="center", fontsize=fontsize, color="darkgrey")

    def __add_text__(self,ax, fraction, text,color='k'):
        ax.text(
            x=0.05, 
            y=0.95, 
            s=text,
            size=8, 
            color='k', 
            ha="left", 
            va="top",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round",fc='white', ec=color)
            )
        return ax       

    def __seal__(self, x:np.float64, integer:int):
        return x if x % integer == 0 else x + integer - x % integer

    def velocity_factor(self, velocity):
        
        compression_time = self.depth*0.72/(0.74*velocity*1000)
        velocity_factor = np.interp(compression_time, 
                                    self._velocity_factor_table[:,0], 
                                    self._velocity_factor_table[:,1], 
                                    right=1.0
                                    )
        return velocity_factor

    def temperature_factor(self, temp):
        
        temperature_factor = np.interp(temp,
                                       self._temperature_factor_table[:,0],
                                       self._temperature_factor_table[:,1],
                                       right=1.0)
        return temperature_factor

    def fender_chart(self, fender_type, energy_scalar=1, reaction_scalar=1, berthing_energy=0.0):

        colors = ['b','g','r','c','m','y','k','w']
        ax_y_titles = ['Energy [kNm]', 'Reaction [kN]']

        fender_properties = np.array([[
            self.depth,
            self.rated_energy*(1-self.energy_tolerance)*energy_scalar,
            self.rated_reaction*(1+self.reaction_tolerance)*reaction_scalar,
        ]]).transpose()

        fender_chart = np.multiply(fender_properties, self._fender_performance).transpose()


        fig, axs = plt.subplots(ncols=(len(ax_y_titles)), nrows=1) 
        fig.suptitle(fender_type)
        #fig.tight_layout()
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = False
        
        for i in range(len(axs)):
            
            deflection = fender_chart[:,0]
            rated_action = fender_chart[:,i+1]
            cubic_interpolation_model = interp1d(deflection, rated_action, kind="cubic")

            _deflection = np.linspace(0, np.max(deflection),500)
            _rated_action = cubic_interpolation_model(_deflection)

            axs[i].plot(_deflection, _rated_action, color=colors[i])

            design_depth = np.max(_deflection)
            rated = np.max(_rated_action)

            rated = self.__seal__(rated, 100) if rated >= 1000 else self.__seal__(rated, 25)


            self.__annotate_axes__(
                ax=axs[i], 
                title='', 
                x_axis='Deflection [mm]', 
                y_axis=ax_y_titles[i],
                xlim=design_depth,
                ylim=rated,
                reverse_x=False,
                reverse_y=True*i
                )
       
        if berthing_energy > 0:
            deflection = np.interp(berthing_energy,fender_chart[:,1],fender_chart[:,0])
            reaction = np.interp(deflection, fender_chart[:,0], fender_chart[:,2])
            
            vals = [berthing_energy, reaction]
            text = [f"Design energy: {int(berthing_energy)}kNm",f"Design reaction: {int(reaction)}kN"]
            y_pos = [berthing_energy/fender_properties[1],reaction/fender_properties[2]]

            for i in range(2):
                axs[i].hlines(vals[i],0,self.depth,linestyles='dashed',label='Design Berthing Energy')
                axs[i] = self.__add_text__(
                    axs[i],
                    y_pos[i],
                    text[i],
                    color=colors[i]
                )
                
                axs[i].vlines(deflection,0,rated,linestyles='dashed')
        plt.show()

        
