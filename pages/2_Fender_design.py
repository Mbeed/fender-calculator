
import streamlit as st
import extra_streamlit_components as stx
import Catalogue
from SCN import SCN
from MV import MV
from Pnuematic import Pnuematic
import numpy as np

fender_types = ["SCN","MV","Pnuematic"]

def first_index(val, search_list):
    index = next(
        (index for index, item in enumerate(search_list) if item > val), None
    )
    return index

def FenderCalc():

    #Create fake fender for capacity reduction factor calcs
    fender_type = fender_selection

    if fender_type == 'SCN':
        return SCN(
            size="SCN300",
            grade=0.9,
            energy_tolerance=manufacturing_tolerance_w,
            reaction_tolerance=manufacturing_tolerance_w
        )
    elif fender_type == 'MV':

        return MV("300x600",
                    "A",
                    2000,
                    manufacturing_tolerance_w,
                    manufacturing_tolerance_w)
        
    elif fender_type == 'Pnuematic':
        return Pnuematic("500x1000",
                        0,
                        manufacturing_tolerance_w,
                        50)
        

def OptimalFender():
    berthing_energy = berthing_energy_w
    design_criteria = design_criteria_w
    selection = selection_w
    fender_type = fender_selection   

    berthing_angle = berthing_angle_w
    velocity = velocity_w
    max_temp = max_temp_w
    
    fender = FenderCalc()
    
    if fender_type == 'MV':
        energy_reduction_factor, reaction_amplification_factor = fender.capacity_factor(
            berthing_angle=berthing_angle_w,
            velocity=velocity_w,
            max_temp=max_temp_w,
            min_temp=min_temp_w,
            bow_flare_angle=0.0
        )    
    else:
        energy_reduction_factor, reaction_amplification_factor = fender.capacity_factor(
            berthing_angle=berthing_angle_w,
            velocity=velocity_w,
            max_temp=max_temp_w,
            min_temp=min_temp_w
        )

    if fender_type == 'SCN':
        design_energies = np.array(Catalogue.SCN_ratings[1])*energy_reduction_factor*(1-manufacturing_tolerance_w/100)

        if design_criteria == 'Depth':
            row = Catalogue.SCN.index(selection)
            col = first_index(berthing_energy, design_energies[row,:])
            if col is not None: 
                results_col.write(f"{selection}-F{Catalogue.SCN_grades[col]}")
            else:
                results_col.write("This size is insufficient, select larger fender.")
        else:
            col = Catalogue.SCN_grades.index(float(selection[1:]))
            row = first_index(berthing_energy, design_energies[:,col])
            if row is not None:
                results_col.write(f"{Catalogue.SCN[row]}-{selection}")
            else: 
                results_col.write(" This grade is insufficient, select higher grade.")

    elif fender_type == 'MV':
        if design_criteria == 'Depth':
            row = Catalogue.MV.index(selection)
            design_energies = [Catalogue.MV_compound_A[row][0],Catalogue.MV_compound_B[row][0]]
            col = first_index(berthing_energy,design_energies)
            if col is not None:
                results_col.write(f"{Catalogue.MV[row]}-{['A','B'][col]}")
            else: 
                results_col.write(" This grade is insufficient, select higher grade.")

        else:    
            if selection == "A":
                design_energies = np.array(Catalogue.MV_compound_A)[0,:]*energy_reduction_factor
            else:
                design_energies = np.array(Catalogue.MV_compound_B)[0,:]*energy_reduction_factor
            row = first_index(berthing_energy, design_energies)
            if row is not None:
                results_col.write(f"{Catalogue.MV[row]}-{selection}")
            else: 
                results_col.write(" This grade is insufficient, select higher grade.")

    elif fender_type == 'Pnuematic':
        if design_criteria == 'Depth':
            iter_list = [50, 80]    
        else:
            iter_list = Catalogue.pnuematic
  
st.set_page_config(
    page_title="Berthing Energy",
    page_icon=":Ring Buoy:",
    layout="centered"
    )

st.write("### Recommended Fender")

fender_selection = stx.tab_bar(data=[
    stx.TabBarItemData(id="SCN", title="SCN",description=""),
    stx.TabBarItemData(id="MV", title="MV", description=""),
    stx.TabBarItemData(id="Pnuematic", title="Pnuematic", description="")
    ])
         

design_criteria_w = st.radio(
    label='Design criteria',
    options=['Depth','Grade'],
    index=0,
    horizontal=True)


design_form = st.form(key="design_form")

with design_form:
    universal_container = st.container(border=False)
    # Universal parameters
    with universal_container:
        col1, col2 = st.columns(2)
        with col1:
            berthing_energy_w = st.number_input(
                label="Berthing Energy",
                value=0.0,
                format="%.1f")
            berthing_angle_w = st.number_input(
                label="Berthing Angle [°]",
                value=0.0,
                format="%.1f")
            velocity_w = st.number_input(
                label="Berthing Velocity [m/s]",
                value=0.1,
                format="%.1f")
        with col2:      
            manufacturing_tolerance_w = st.number_input(
                label="Manufacturing Tolerance [%]",
                value=10)
            max_temp_w = st.number_input(
                label="Max Temperature [°C]",
                value=23.0,
                format="%.1f")
            min_temp_w = st.number_input(
                label="Min Temperature [°C]",
                value=23.0,
                format="%.1f")

    if fender_selection == 'SCN':
        if design_criteria_w == 'Depth':
            selection_w = st.selectbox(
                label="Fender Depth",
                options=Catalogue.SCN)
        else:
            selection_w = st.selectbox(
                label="Fender Grade",
                options=list(map(lambda orig_string: f"F{orig_string}",Catalogue.SCN_grades)))  
    elif fender_selection == 'MV':
        if design_criteria_w == 'Depth':
            selection_w = st.selectbox(
                label="Fender Depth",
                options=Catalogue.MV)
        else:    
            selection_w = st.selectbox(
                label="Fender Compound",
                options=['A','B'])
    elif fender_selection == 'Pnuematic':
        if design_criteria_w == 'Depth':
            selection_w = st.selectbox(
                label="Fender Diameter",
                options=Catalogue.pnuematic)
        else:
            selection_w = st.selectbox(
                label="Fender Pressure",
                options=[50, 80])
    else:
        st.warning("Please select a fender")

    calc_col, results_col= st.columns([1,3])

    with calc_col:
        calculate_btn = st.form_submit_button("Calculate")


    if calculate_btn:
        OptimalFender()
