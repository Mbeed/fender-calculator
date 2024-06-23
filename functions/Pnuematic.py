from Fender import Fender
import numpy as np
import Catalogue as Catalogue
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d 

class Pnuematic(Fender):

    def __init__(self, size, energy_tolerance, reaction_tolerance, pressure) -> None:

        self.size = size
        self.pressure = pressure
        depth = int(str.split(size,"x")[0])
        rated_energy, rated_reaction, rated_hull_pressure = self.__get_rated_capacities__()
        super().__init__(depth, rated_reaction, rated_energy, energy_tolerance, reaction_tolerance)
        self.rated_hull_pressure = rated_hull_pressure
        
        self._fender_performance = np.array([
            [0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6],
            [0,0.01,0.02,0.04, 0.07, 0.11, 0.17,0.24,0.33, 0.44,0.59,0.77,1],
            [0, 0.03, 0.06, 0.1, 0.14, 0.19, 0.25, 0.32, 0.4, 0.51, 0.66, 0.82, 1],
            [0.4, 0.405, 0.41, 0.42, 0.44, 0.46, 0.49, 0.54, 0.6, 0.67, 0.76, 0.81, 1]
        ])
        
    def __get_rated_capacities__(self):
        row = Catalogue.pnuematic.index(self.size)
        pnuematic_ratings = Catalogue.pnuematic_50 if self.pressure == 50 else Catalogue.pnuematic_80

        rated_energy = pnuematic_ratings[row][0]
        rated_reaction = pnuematic_ratings[row][1]        
        rated_hull_pressure = pnuematic_ratings[row][2]
        return rated_energy, rated_reaction, rated_hull_pressure

    def capacity_factor(self, berthing_angle, velocity, max_temp, min_temp):

        energy_factor = (1.0-self.energy_tolerance)
        reaction_factor = (1.0+self.reaction_tolerance)
        
        return energy_factor, reaction_factor
    
    def fender_chart(self, berthing_energy=0):

        colors = ['b','g','r','c','m','y','k','w']
        ax_y_titles = ['Energy [kNm]', 'Reaction [kN]', 'Pressure [kPa]']
        fender_properties = np.array([[
            self.depth,
            self.rated_energy*(1-self.energy_tolerance),
            self.rated_reaction*(1+self.reaction_tolerance),
            self.rated_hull_pressure
        ]]).transpose()

        fender_chart = np.multiply(fender_properties, self._fender_performance).transpose()
        
        fig, axs = plt.subplots(ncols=(len(ax_y_titles)), nrows=1) 
        fig.suptitle(f"{self.size}-{self.pressure}kPa")
        #fig.tight_layout()
        
        for i in range(len(axs)):
            deflection = fender_chart[:,0]
            rated_action = fender_chart[:,i+1]
            cubic_interpolation_model = interp1d(deflection, rated_action, kind="cubic")

            _deflection = np.linspace(0, np.max(deflection),500)
            _rated_action = cubic_interpolation_model(_deflection)

            xlim = np.max(_deflection)
            ylim = np.max(_rated_action)

            ylim = super().__seal__(ylim, 100) if ylim >= 1000 else super().__seal__(ylim, 25)

            axs[i].plot(_deflection, _rated_action, color=colors[i])
            super().__annotate_axes__(axs[i], '', 'Deflection [mm]', ax_y_titles[i], xlim, ylim)
       
        if berthing_energy > 0:
            deflection = np.interp(berthing_energy,fender_chart[:,1],fender_chart[:,0])
            reaction = np.interp(deflection, fender_chart[:,0], fender_chart[:,2])
            pressure = np.interp(deflection,fender_chart[:,0],fender_chart[:,3])

            vals = [berthing_energy, reaction, pressure]
            text = [f"Design energy: {int(berthing_energy)}kNm",f"Design reaction: {int(reaction)}kN",f"Design pressure: {int(pressure)}kPa"]
            y_pos = [berthing_energy/fender_properties[1],reaction/fender_properties[2],pressure/fender_properties[3]]

            for i in range(3):
                axs[i].hlines(vals[i],0,self.depth,linestyles='dashed',label='Design Berthing Energy')
                axs[i] = self.__add_text__(
                    axs[i],
                    y_pos[i],
                    text[i],
                    color=colors[i]
                )
                
                axs[i].vlines(deflection,0,axs[i].get_ylim()[1],linestyles='dashed')


if __name__ == "__main__":

    test_p = Pnuematic('1700x3000', 0, 0.1, 50)
    test_p.fender_chart(100)
