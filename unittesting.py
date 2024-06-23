import unittest
import functions.Berthing as Berthing
import numpy as np
from functions.MV import MV
from functions.SCN import SCN
from functions.Pnuematic import Pnuematic

#Berthing energy calculation package testing. Uses inputs from PIANC WG 33 Appendix case study. 
#Note, not all values within this example are correct.
class BerthingTestCalculations(unittest.TestCase):

    def setUp(self) -> None:
        # Vessel paramaters
        self.DWT = 39000
        self.draft = 10.9
        self.beam = 26.4
        self.LBP = 170
        self.UKC = 3

        #Factors
        self.Cb = 0.77
        self.Cm = 1.84
        self.Ce = 0.5

        # Berthing parameters
        self.abnormal_factor = 1.75
        self.velocity = 0.1
        self.berthing_point = 0.25 #25%
        self.berthing_angle = 5

    def test_block_coefficient(self) -> None:
        
        val = Berthing.BlockCoefficient(
            displacement=self.DWT,
            LBP=self.LBP,
            beam=self.beam,
            draft=self.draft
        )
        
        self.assertAlmostEqual(
            val,0.77,2,f"Block coefficient is not correct.\nCalculated {val:.2f}, should be {0.77}")
        
    def test_eccentricity_coefficient(self) -> None:
        #This one uses a vessel from Shibata Fender Design manual

        val = Berthing.EccentricityCoefficient(
            Cb=0.796,
            LBP=236,
            beam=43,
            berthing_point=1/3,
            berthing_angle=np.deg2rad(5),
            velocity_angle=0
        )

        self.assertAlmostEqual(
            val,0.761,2,f"Eccentricity coefficient is not correct.\nCalculated {val:.2f}, should be {0.76}")
    
    def test_added_mass_shigeru(self) -> None:
        
        val = Berthing.MassCoefficient(
            draft=self.draft,
            beam=self.beam,
            UKC=self.UKC,
            Cb=self.Cb,
            calculation_type="Shigeru"
        )

        self.assertAlmostEqual(
            val, 1.84, 2, f"Shigeru Added Mass coefficient is not correct.\nCalculated {val:.2f}, should be {1.84}"
        )

    def test_added_mass_vasco(self) -> None:
        
        val = Berthing.MassCoefficient(
            draft=self.draft,
            beam=self.beam,
            UKC=self.UKC,
            Cb=self.Cb,
            calculation_type="Vasco Costa"
        )

        self.assertAlmostEqual(
            val, 1.83, 2, f"Vasco Costa Added Mass coefficient is not correct.\nCalculated {val}, should be {1.84}"
        )

    def test_added_mass_pianc(self) -> None:
        
        val = Berthing.MassCoefficient(
            draft=self.draft,
            beam=self.beam,
            UKC=self.UKC,
            Cb=self.Cb,
            calculation_type="PIANC"
        )

        self.assertAlmostEqual(
            val, 1.67, 2, f"PIANC Added Mass coefficient is not correct.\nCalculated {val}, should be {1.84}"
        )

    def test_berthing_energy(self) -> None:

        val = Berthing.BerthingEnergy(
            berthing_velocity=self.velocity,
            berthing_angle=self.berthing_angle,
            displacement=self.DWT,
            LBP=self.LBP,
            beam=self.beam,
            draft=self.draft,
            UKC=self.UKC,
            berthing_point=self.berthing_point,
            mass_calc="Shigeru"
        )*self.abnormal_factor

        self.assertAlmostEqual(
            first=val, 
            second=351,
            msg=f"Berthing energy is not correct.\nCalculated {val:.1f}kNm, should be {351.6}kNm",
            delta=5
        )
    
class SCNTestCalculations(unittest.TestCase):

    def setUp(self) -> None:
        self.fender = SCN(
            size="SCN1050",
            grade=1.1,
            energy_tolerance=0.1,
            reaction_tolerance=0.1,
            material="Blend"
        )
        
    def test_angle_factor(self):
        energy, reaction = self.fender.angle_factor(5)

        self.assertAlmostEqual(
            first=energy,
            second=1.055,
            places=3,
            msg=f"Energy factor is not correct.\nCalculated {energy:.1f}, should be {1.055}"
        )

        self.assertAlmostEqual(
            first=reaction,
            second=1.000,
            places=3,
            msg=f"Reaction factor is not correct.\nCalculated {reaction:.1f}, should be {1.000}"
        )

    def test_temperature_factor(self):
        temp_factor = self.fender.temperature_factor(40)

        self.assertAlmostEqual(
            first=temp_factor,
            second=0.947,
            places=3,
            msg=f"Temperature factor is not correct.\nCalculated {temp_factor:.1f}, should be {0.947}"
        )
    
    def test_velocity_factor(self):
        velocity_factor = self.fender.velocity_factor(0.1)

        self.assertAlmostEqual(
            first=velocity_factor,
            second=1.07,
            places=2,
            msg=f"Velocity factor is not correct.\nCalculated {velocity_factor:.1f}, should be {1.07}"
        )            

    def test_capacities(self):
        energy, reaction = self.fender.__get_rated_capacities__()

        self.assertAlmostEqual(
            first=energy,
            second=446.6,
            places=1,
            msg=f"Energy capacity is not correct.\nCalculated {energy:.1f}, should be {446.6}"
        )

        self.assertAlmostEqual(
            first=reaction,
            second=713.4,
            places=1,
            msg=f"Reaction is not correct.\nCalculated {reaction:.1f}, should be {713.4}"
        )

class MVTestCalculations(unittest.TestCase):
    def setUp(self):
        self.fender = MV(
            size='1000x1000',
            compound="B",
            leg_spacing=2000
        )
    
    

if __name__ == '__main__':
    unittest.main()