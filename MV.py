from Fender import Fender
import Catalogue
import numpy as np
from scipy.interpolate import LinearNDInterpolator

class MV(Fender):

    def __init__(self, size, compound, leg_spacing, energy_tolerance=0.1, reaction_tolerance=0.1) -> None:

        self.size = size
        self.compound = compound
        self.leg_spacing = leg_spacing
        
        dims = str.split(size,"x")
        depth = int(dims[0])
        self.length = int(dims[1])

        rated_energy, rated_reaction = self.__get_rated_capacities__()
        super().__init__(depth, rated_reaction, rated_energy, energy_tolerance, reaction_tolerance)
        
        self._fender_performance = np.array([
            [0,0.050,0.100,0.150,0.200,0.280,0.350,0.400,0.450,0.500,0.575,0.625],
            [0,0.020,0.070,0.140,0.240,0.410,0.560,0.660,0.760,0.850,1.000,1.130],
            [0,0.310,0.580,0.780,0.920,1.000,0.960,0.900,0.850,0.840,1.000,1.300]
        ])
        

        self._transverse_reduction = np.array([
            [1.00,0.980,0.960,0.900],
            [1.00,0.970,0.910,0.830],
            [1.00,0.950,0.875,0.750],
            [1.00,0.925,0.790,0.630]
        ]).flatten()

        self._longitudinal_reduction = np.array([
            [0.990,0.990,0.930,0.880],
            [0.990,0.970,0.860,0.730],
            [0.990,0.850,0.640,0.500],
            [0.950,0.620,0.290,0.200]
        ]).flatten()

    def temperature_factor(self, temp):
        return super().temperature_factor(temp)
    
    def velocity_factor(self, velocity):
        return super().velocity_factor(velocity)

    def angle_factor(self, transverse_angle, longitudinal_angle):
        transverse_ratio = min(self.leg_spacing/self.depth,2.0)
        longitudinal_ratio = min(self.length/self.depth,4.0)
        
        trans_axes = list(zip(
            np.array([0,5,10,15]*4), 
            np.repeat([1.2,1.4,1.6,2.0],4))
            )
        
        long_axes = list(zip(
            np.array([0,5,10,15]*4), 
            np.repeat([0.625,1.000,2.000,4.000],4))
            )
        
        trans_factor = LinearNDInterpolator(trans_axes,self._transverse_reduction)(transverse_angle, transverse_ratio)
        long_factor = LinearNDInterpolator(long_axes,self._longitudinal_reduction)(longitudinal_angle, longitudinal_ratio)

        return trans_factor*long_factor
               
    def __get_rated_capacities__(self):
        row = Catalogue.MV.index(self.size)
        MV_ratings = Catalogue.MV_compound_A if self.compound == "A" else Catalogue.MV_compound_A

        rated_energy = MV_ratings[row][0]*self.length/1000
        rated_reaction = MV_ratings[row][1]*self.length/1000        

        return rated_energy, rated_reaction

    def capacity_factor(self, berthing_angle, bow_flare_angle, velocity, max_temp,min_temp):

        energy_angle_factor = self.angle_factor(berthing_angle, bow_flare_angle)
        velocity_factor = self.velocity_factor(velocity)
        energy_temperature_factor = self.temperature_factor(max_temp)
        reaction_temperature_factor = self.temperature_factor(min_temp)

        energy_factor = energy_angle_factor*velocity_factor*energy_temperature_factor
        reaction_factor = velocity_factor*reaction_temperature_factor
        
        return energy_factor, reaction_factor

    def fender_chart(self, berthing_angle=0.0, bow_flare_angle=0.0, velocity=0.01, max_temperature=23.0, min_temperature=23.0, berthing_energy=0.0):
        factors = self.capacity_factor(berthing_angle, bow_flare_angle, velocity, max_temperature, min_temperature)


        return super().fender_chart(
            fender_type=f"{self.size}-Compound {self.compound}", 
            energy_scalar=factors[0], 
            reaction_scalar=factors[1],
            berthing_energy=berthing_energy
        )
    
if __name__ == "__main__":

    test_p = MV("500x2000", "A", 1000)
    #test_p.angle_factor(5,5)

    test_p.fender_chart()
