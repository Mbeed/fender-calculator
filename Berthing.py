import numpy as np
import pandas as pd

rho_w = 1.025 #kN/m3

def BlockCoefficient(displacement:float, LBP:float, beam:float, draft:float):
    Cb = displacement/(1.025*LBP*beam*draft)
    return Cb

def K_gyration(Cb:float, LBP:float):
    return (0.19*Cb+0.11)*LBP

def Gamma(beam:float, berthing_point:float, berthing_angle:float, velocity_angle:float):
    #TODO: Revist this, add hull radius
    """Returns angle between velocity vector and berthing point.

    Parameters
    ----------
    beam : float
        Vessel beam in meters.
    berthing_angle : float
        Berthing angle of vessel relative to berth in radians.
    velocity_angle : float
        Velocity angle of vessel relative to berth in radians.
    hull_radius : float
        Radius of bow hull in meters.
    
    Returns
    -------
    float
        Gamma angle in radians.

    """
    
    gamma = np.pi/2-berthing_angle-velocity_angle-np.arctan((0.5*beam/berthing_point))
    return gamma

def EccentricityCoefficient(gamma:float, radius_of_gyration:float, lever_arm:float):
    
    Ce = (
        (np.power(radius_of_gyration,2)+np.power(radius_of_gyration*np.cos(gamma),2))/
        (np.power(radius_of_gyration,2)+np.power(lever_arm,2))
        )
    return Ce

def MassCoefficient(draft:float, UKC:float=None, beam:float=None, calculation_type:float="Vasco Costa"):
    calculation_types = ["PIANC", "Shigeru","Vasco Costa"]
    Cm = 0

    if not calculation_type in calculation_types:
        raise ValueError(f"""Software does not currently support {calculation_type} method""")
    elif calculation_type == "PIANC":
        Cm = np.minimum(1.8,np.maximum(1.5,1.875-0.75*UKC/draft))
    elif calculation_type == "Shigeru":
        Cm = 1+np.pi*draft/(2*beam)
    elif calculation_type == "Vasco Costa":
        Cm = 1+2*(draft/beam)
    
    return Cm 
                   
def BerthingEnergy(berthing_velocity, berthing_angle, velocity_angle, displacement,
                   LBP, beam, draft, UKC, berthing_point, softness_coefficient, 
                   configuration_coefficient, mass_calc="Vasco Costa", output = False) -> str|float:

    #convert degrees into radians
    berthing_angle = np.deg2rad(berthing_angle)
    velocity_angle = np.deg2rad(velocity_angle)

    Cb = BlockCoefficient(displacement, LBP, beam, draft)
    K = K_gyration(Cb, LBP)
    gamma = Gamma(beam, berthing_point, berthing_angle, velocity_angle)
    Ce = EccentricityCoefficient(gamma, K, berthing_point)
    Cm = MassCoefficient(draft, UKC, beam, calculation_type=mass_calc)
    Cs = softness_coefficient
    Cc = configuration_coefficient
    berthing_energy = 0.5*displacement*Cm*Ce*Cs*Cc*np.power(berthing_velocity*np.cos(velocity_angle),2)
    
    message = f"""Calculation out:\n
                    \tBerthing energy: {berthing_energy:.2f}kNm\n
                    \tBlock coefficient [Cb]:{Cb:.2f}\n
                    \tK factor [K]: {K:.2f}\n
                    \tGamma angle [gamma]: {np.rad2deg(gamma):.2f}\n
                    \tEccentricity coefficient [Ce]: {Ce:.2f}\n
                    \tMass coefficient [Cm]: {Cm:.2f}\n
                    \tSoftness coefficient [Cs]: {Cs:.2f}\n
                    \tConfiguration coefficient [Cc]: {Cc:.2f}
                    """
    if output:
        return message
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


    
