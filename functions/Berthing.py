import numpy as np
import pandas as pd

rho_w = 1.03 #kN/m3

def BlockCoefficient(displacement:float, LBP:float, beam:float, draft:float):
    Cb = displacement/(rho_w*LBP*beam*draft)
    return Cb

def BowRadius(Cb:float, LOA:float, beam:float):
    x = 0
    if Cb < 0.6: x = 0.3*LOA
    elif Cb >= 0.8: x = 0.2*LOA
    else: x = 0.25*LOA

    return (x^2/beam+beam/4)

def EccentricityCoefficient(Cb:float, LBP: float, beam:float, berthing_point:float,
                            berthing_angle:float, velocity_angle:float=0) -> float:
    K = (0.19*Cb+0.11)*LBP
    R = np.sqrt(np.square((0.5-berthing_point)*LBP)+np.square(0.5*beam))
    gamma = np.pi/2-berthing_angle-np.arcsin(0.5*beam/R)-velocity_angle
    Ce = (np.square(K)+np.square(R*np.cos(gamma)))/(np.square(K)+np.square(R))
        
    return Ce

def MassCoefficient(draft:float, UKC:float, beam:float, Cb:float,
                    calculation_type:float="Shigeru") -> float:
    calculation_types = ["PIANC", "Shigeru","Vasco Costa"]

    if not calculation_type in calculation_types:
        raise ValueError(f"""Software does not currently support {calculation_type} method""")
    elif calculation_type == "PIANC":
        return np.minimum(1.8,np.maximum(1.5,1.875-0.75*UKC/draft))
    elif calculation_type == "Shigeru":
        return 1+np.pi*draft/(2*beam*Cb)
    elif calculation_type == "Vasco Costa":
        return 1+2*(draft/beam)   
                   
def BerthingEnergy(berthing_velocity, berthing_angle,displacement,LBP, 
                    beam, draft, UKC, berthing_point, softness_coefficient=1.0, 
                    configuration_coefficient=1.0,  velocity_angle=0, mass_calc="Vasco Costa", output = False) -> float:

    #convert degrees into radians
    berthing_angle = np.deg2rad(berthing_angle)
    velocity_angle = np.deg2rad(velocity_angle)

    Cb = BlockCoefficient(displacement, LBP, beam, draft)
    Ce = EccentricityCoefficient(Cb, LBP, beam, berthing_point, berthing_angle, velocity_angle)
    Cm = MassCoefficient(draft, UKC, beam, Cb, calculation_type=mass_calc)
    Cs = softness_coefficient
    Cc = configuration_coefficient
    berthing_energy = 0.5*displacement*Cm*Ce*Cs*Cc*np.square(berthing_velocity*np.cos(velocity_angle))
    
    if output:
        return f"""Calculation out:\n
                    \tBerthing energy: {berthing_energy:.2f}kNm\n
                    \tBlock coefficient [Cb]:{Cb:.2f}\n
                    \tEccentricity coefficient [Ce]: {Ce:.2f}\n
                    \tMass coefficient [Cm]: {Cm:.2f}\n
                    \tSoftness coefficient [Cs]: {Cs:.2f}\n
                    \tConfiguration coefficient [Cc]: {Cc:.2f}
                    """
    else:
        return berthing_energy


if __name__ == "__main__":
    berthing_velocty = 0.4 #m/s
    berthing_angle = 15 #°
    velocity_angle = 0 #°
    displacement = 54 #t
    LOA = 25 #m
    beam = 8.5 #m
    draft = 1.8 #m
    UKC = 0.5 #m
    
    berthing_point = 0.25*LOA

    berthing = BerthingEnergy(
        berthing_velocity=0.4,
        berthing_angle=15,
        velocity_angle=0,
        displacement=54,
        LBP=25,
        beam=8.5,
        draft=1.8,
        UKC=0.5,
        berthing_point=0.25*25,
        softness_coefficient=1.0,
        configuration_coefficient=1.0,
        mass_calc="PIANC",
        output=True) 
    print(berthing)


    
