import streamlit as st
import functions.Berthing as Berthing

berthing_point = {
    "1/6 point": 0.333,
    "1/5 point": 0.3,
    "1/4 point": 0.25,
    "1/3 point": 0.1667
}
st.set_page_config(
    page_title="Berthing Energy",
    page_icon=":boat:",
    layout="centered"
    )
st.sidebar.image("static/WGA_LOGO-RGB-PRIMARY_RED.png")
st.write("# Berthing Energy")

def BerthingEnergy():
    try:
        abnormal_factor = abnormal_factor_w
        berthing_point_val = berthing_point.get(berthing_point_w)*LBP_w
        normal_energy = Berthing.BerthingEnergy(
            berthing_velocity=velocity_w,
            berthing_angle=berthing_angle_w,
            velocity_angle=velocity_angle_w,
            displacement=displacement_w,
            beam=beam_w,
            LBP=LBP_w,
            draft=draft_w,
            UKC=UKC_w,
            berthing_point=berthing_point_val,
            #hull_radius=hull_radius_w.value,
            softness_coefficient=softness_coefficient_w,
            configuration_coefficient=configuration_coefficient_w,
            mass_calc=mass_calc_w,
            output=False
        )
        design_energy = normal_energy*abnormal_factor

        if mass_calc_w == "Vasco Costa" and (
            velocity_w < 0.08 or 
            UKC_w < 0.1*draft_w):
                st.write("Vasco Costa is valid for UKC>=0.1*Draft and Berthing Velocity > 0.08m/s")

        result_col2.write(f"Normal energy: {normal_energy:.2f}kNm")
        result_col3.write(f"Abnormal energy: {design_energy:.2f}kNm")


    except ZeroDivisionError:
        st.write("Design inputs are incomplete. Review chosen values.")


berthing_energy_form = st.form(key="energy_form")

with berthing_energy_form:
    #Mass coefficient method
    mass_calc_w = st.selectbox(
        label='Mass coefficient method',
        options=['Vasco Costa','Shigeru','PIANC']
        )
    
    result_col1, result_col2, result_col3 = st.columns(
        spec=[2,3,3])
    
    #Calculate button
    submitted = result_col1.form_submit_button(
        label="Calculate")

    energy_tab1, energy_tab2, energy_tab3 = st.tabs(["Berthing Event","Vessel Particulars","Berthing Coefficients"])

    #Berthing event parameters
    with energy_tab1:
        berthing_angle_w = st.number_input(
            label="Berthing angle [°]",
            min_value=0.0,
            value=5.0,
            step=0.1,
            format="%.1f")
        velocity_w = st.number_input(
            label="Berthing velocity [m/s]",
            min_value=0.00,
            value=0.20,
            step=0.01,
            format="%.2f")
        velocity_angle_w = st.number_input(
            label="Velocity angle [°]",
            min_value=0.0,
            step=0.1,
            format="%.1f")
        berthing_point_w = st.select_slider(
            label="Berthing point",
            options=berthing_point.keys())

    #Vessel particulars
    with energy_tab2:
        col1, col2 = st.columns(2)
        with col1:
            displacement_w = st.number_input(
                label="Displacement [t]",
                value=3500,
                step=10)
            LBP_w = st.number_input(
                label="LBP [m]",
                value=81.7,
                step=0.1,
                format="%.1f")
            beam_w = st.number_input(
                label="Beam [m]",
                value=18.0,
                step=0.1,
                format="%.1f")
        with col2:
            draft_w = st.number_input(
                label="Draft [m]",
                value=7.0,
                step=0.1,
                format="%.1f")
            UKC_w = st.number_input(
                label="UKC [m]",
                value=4.42,
                step=0.01,
                format="%.2f")
            hull_radius_w = st.number_input(
                label="Hull radius [m]",
                value=20.6,
                step=0.1,
                format="%.1f")

    #Berthing coefficients
    with energy_tab3:
        softness_coefficient_w = st.number_input(
            label="Softness coefficient [Cs]",
            value=1.0,
            step=0.1,
            format="%.1f")
        configuration_coefficient_w = st.number_input(
            label="Configuration coefficient [Cc]",
            value=1.0,
            step=0.1,
            format="%.1f")
        abnormal_factor_w = st.number_input(
            label="Abnormal Factor",
            value=2.0,
            step=0.1,
            format="%.1f")

    if submitted:
        BerthingEnergy()

