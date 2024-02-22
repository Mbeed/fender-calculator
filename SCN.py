from Fender import Fender
import Catalogue
import numpy as np

class SCN(Fender):

    def __init__(self, size, grade, energy_tolerance, reaction_tolerance, material="Blend") -> None:

        depth = int(size[3:])
        self.size = size
        self.grade = grade
        self.material = material
        
        rated_reaction, rated_energy = self.__get_rated_capacities__()
        super().__init__(depth, rated_reaction, rated_energy, energy_tolerance, reaction_tolerance)


        self._fender_performance = np.array([
            [0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.72,0.75],
            [0,0.01,0.04,0.08,0.15,0.22,0.31,0.4,0.5,0.59,0.67,0.75,0.82,0.89,0.96,1.00,1.06],
            [0,0.20,0.39,0.58,0.76,0.90,0.98,1.00,0.98,0.94,0.9,0.88,0.88,0.90,0.96,1.00,1.10]
        ])
    
        self._temperature_factor_table = np.array([
            [-30.0,-20.0,-10.0,0.000,10.00,23.00,30.00,40.00,50.00],
            [1.540,1.249,1.130,1.075,1.030,1.000,0.978,0.947,0.916],
            [1.315,1.142,1.080,1.053,1.025,1.000,0.978,0.946,0.914],
            [1.877,1.410,1.206,1.108,1.038,1.000,0.979,0.948,0.918]
        ]).transpose()

        
        self._velocity_factor_table = np.array([
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
            [1.20,1.16,1.14,1.13,1.11,1.10,1.09,1.09,1.08,1.07,1.07,1.06,1.06,1.05,1.05,1.05,1.04,1.04,1.04,1.03],
            [1.14,1.10,1.09,1.07,1.06,1.06,1.05,1.04,1.04,1.03,1.03,1.02,1.02,1.02,1.01,1.01,1.01,1.01,1.00,1.00],
            [1.31,1.25,1.22,1.20,1.19,1.17,1.16,1.15,1.14,1.14,1.13,1.12,1.12,1.11,1.11,1.10,1.10,1.09,1.09,1.08]
        ]).transpose()

        self._angle_factor_table = np.array([
            [0.000,3.000,5.000,8.000,10.00,15.00,20.00],
            [1.000,1.039,1.055,1.029,1.000,0.856,0.739],
            [1.000,1.000,1.000,1.000,1.000,0.950,0.800]
        ]).transpose()
    
    def __get_rated_capacities__(self):
    
        row = Catalogue.SCN.index(self.size)
        col = Catalogue.SCN_grades.index(self.grade)

        rated_energy = Catalogue.SCN_ratings[0][row][col]
        rated_reaction = Catalogue.SCN_ratings[1][row][col]

        return rated_reaction, rated_energy

    def angle_factor(self, berthing_angle):
        
        energy_angle_factor = np.interp(berthing_angle,
                                        self._angle_factor_table[:,0],
                                        self._angle_factor_table[:,1],
                                        right=0.739
                                        )
        reaction_angle_factor = np.interp(berthing_angle,
                                          self._angle_factor_table[:,0],
                                          self._angle_factor_table[:,2],
                                          right=0.8)
        return energy_angle_factor, reaction_angle_factor

    def velocity_factor(self, velocity):
        material_types = ["Blend", "Rubber", "Synthetic"]
        i = material_types.index(self.material)

        compression_time = self.depth*0.72/(0.74*velocity*1000)
        
        velocity_factor = np.interp(compression_time, 
                                    self._velocity_factor_table[:,0], 
                                    self._velocity_factor_table[:,i+1], 
                                    right=1.0
                                    )
        return velocity_factor

    def temperature_factor(self, temp):
        material_types = ["Blend", "Rubber", "Synthetic"]
        i = material_types.index(self.material)

        temperature_factor = np.interp(temp,
                                       self._temperature_factor_table[:,0],
                                       self._temperature_factor_table[:,i+1]
                                       )
        return temperature_factor

    def capacity_factor(self, berthing_angle, velocity, max_temp, min_temp):

        energy_angle_factor, reaction_angle_factor = self.angle_factor(berthing_angle)
        velocity_factor = self.velocity_factor(velocity)
        energy_temperature_factor = self.temperature_factor(max_temp)
        reaction_temperature_factor = self.temperature_factor(min_temp)


        energy_factor = energy_angle_factor*velocity_factor*energy_temperature_factor
        reaction_factor = reaction_angle_factor*velocity_factor*reaction_temperature_factor
        
        return energy_factor, reaction_factor
        
    def fender_chart(self, berthing_angle=0.0, velocity=0.01, max_temperature=23.0, min_temperature=23.0, berthing_energy=0.0):

        factors = self.capacity_factor(berthing_angle, velocity, max_temperature, min_temperature)

        return super().fender_chart(
            fender_type=f"{self.size}-F{self.grade}", 
            energy_scalar=factors[0], 
            reaction_scalar=factors[1],
            berthing_energy=berthing_energy
        )

if __name__ == "__main__":

    test_p = SCN("SCN700", 1.7,0.1, 0.1)
    print(test_p.velocity_factor(0.2))
    #fig = test_p.fender_chart(250)
