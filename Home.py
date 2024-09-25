import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon=":house:",
    layout="centered"
)

st.write("# Fender Design Calculator")

st.sidebar.image("static/KF-Reversed-Stacked-SolidCMYK.jpg")

st.markdown(
    """
    This tool is intended to be used to calculate berthing energy and to optimise the design of fenders.
    Currently supported fender types include ***SCN, MV, Pnuematic***.

    ### Source documentation
    - Git source code [Git](https://gitlab.com/memphot1/fender-calculator)
    """
)