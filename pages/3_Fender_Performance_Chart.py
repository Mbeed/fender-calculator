
import streamlit as st
import extra_streamlit_components as stx
import functions.Catalogue as Catalogue
from functions.SCN import SCN
from functions.MV import MV
from functions.Pnuematic import Pnuematic
import numpy as np

st.set_page_config(
    page_title="Berthing Energy",
    page_icon=":Ring Buoy:",
    layout="centered"
    )

fender_types = ["SCN","MV","Pnuematic"]
   


def FenderCalc():

    fender_type = fender_selection
    manufacturing_tolerance = manufacturing_tolerance_w/100

    if fender_type == 'SCN':
        size = SCN_w
        grade = SCN_grade_w
        material = SCN_material_w
        fender = SCN(size,
                    grade,
                    manufacturing_tolerance,
                    manufacturing_tolerance, 
                    material)
        #energy_factor, reaction_factor = fender.capacity_factor(berthing_angle, velocity, temp)
        return fender
        
    elif fender_type == 'MV':
        size = MV_w
        compound = MV_compound_w
        leg_spacing = MV_unit_spacing_w

        fender = MV(size,
                    compound,
                    leg_spacing,
                    manufacturing_tolerance,
                    manufacturing_tolerance)
        return fender
        
    elif fender_type == 'Pnuematic':
        size = pnuematic_w
        pressure = pnuematic_pressure_w
        fender = Pnuematic(size,
                        0,
                        manufacturing_tolerance,
                        pressure)
        return fender
    

def FenderChart():
    fender = FenderCalc()
    berthing_energy = berthing_energy_w
    berthing_angle = berthing_angle_w
    velocity = velocity_w
    max_temp = max_temp_w
    min_temp = min_temp_w

    design_fender = fender_selection 

    if design_fender =="MV":
        energy_factor, reaction_factor = fender.capacity_factor(
            berthing_angle = berthing_angle,
            bow_flare_angle = MV_bow_flare_w,
            velocity=velocity,
            max_temp=max_temp,
            min_temp=min_temp
        )   
    else:
        energy_factor, reaction_factor = fender.capacity_factor(
            berthing_angle = berthing_angle,
            velocity=velocity,
            max_temp=max_temp,
            min_temp=min_temp
        )
    #TODO add back in capacity factor. It's in SCN section below
    if berthing_energy > energy_factor*fender.rated_energy:
        chart_container.warning("Rated capacity of the fender is exceeded. Select another size or grade.")
    elif design_fender == "MV":
        flare_angle = MV_bow_flare_w
        chart_container.pyplot(
        fig=fender.fender_chart(berthing_angle, flare_angle, velocity, max_temp, min_temp, berthing_energy),
        use_container_width=True
        )
    elif design_fender == "Pnuematic":
        chart_container.pyplot(
        fig=fender.fender_chart(berthing_energy),
        use_container_width=True
        ) 
    else:
        chart_container.pyplot(
        fig=fender.fender_chart(berthing_angle, velocity, max_temp, min_temp, berthing_energy),
        use_container_width=True
        )


st.set_option('deprecation.showPyplotGlobalUse', False)
st.sidebar.image("static/WGA_LOGO-RGB-PRIMARY_RED.png")

st.write("# Fender Design")
fender_selection = stx.tab_bar(data=[
    stx.TabBarItemData(id="SCN", title="SCN",description=""),
    stx.TabBarItemData(id="MV", title="MV", description=""),
    stx.TabBarItemData(id="Pnuematic", title="Pnuematic", description="")
    ])


fender_form = st.form(key="fender_form",border=False)


with fender_form:          
    universal_container = st.container(border=True)
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
    #Calculate button
    fender_container = st.container(border=True)

    
    # SCN
    if fender_selection=="SCN":
        SCN_w = fender_container.selectbox(
            label='Choose Fender:',
            options=Catalogue.SCN,
            index=0)
        SCN_grade_w = fender_container.selectbox(
            label='Choose Fender Grade:',
            options=Catalogue.SCN_grades,
            index=0)
        SCN_material_w =fender_container.selectbox(
            label="Choose fender material:", 
            options=["Blend", "Rubber", "Synthetic"],
            index=0)

    # MV
    elif fender_selection=="MV":
        MV_w = fender_container.selectbox(
            label='Choose Fender',
            options=Catalogue.MV,
            index=0)
        MV_compound_w = fender_container.selectbox(
            label='Choose Compound Type',
            options=['A','B'],
            index=0)
        MV_unit_spacing_w = fender_container.number_input(
            label="Unit spacing [mm]",
            min_value=0,
            value=2000,
            step=1)
        MV_bow_flare_w = fender_container.number_input(
            label="Bow Flare angle [°]",
            min_value=0.0,
            value=5.0,
            step=0.1,
            format="%.2f")

    # Pnuematic
    elif fender_selection=="Pnuematic":
        pnuematic_w = fender_container.selectbox(
            label='Choose Fender',
            options=Catalogue.pnuematic,
            index=0)
        pnuematic_pressure_w = fender_container.selectbox(
            label='Choose inflation pressure',
            options=[50, 80],
            index=0)

    else:
        fender_container.warning("Please select a fender")

    submitted = fender_container.form_submit_button(
        label="Calculate")
    chart_container = st.container()


    if submitted:
        FenderChart()
