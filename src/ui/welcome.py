import streamlit as st


def main(state):

    # couldn't import md file
    st.title(":wave: Welcome!")

    st.header("Introduction")
    st.write("As people around the world began to transition back into the normal lives they had before the COVID-19 pandemic, many would like to get vaccinated to ensure their own and other's safety from the deadly virus. Although the vaccine has been tested, there are still some things to be skeptical of; one being the wide range of possible symptoms or side effects that could occur when taking the newly approved vaccine. Vaccine data has been collected and shared publicly online, but it can be difficult to visualize or understand.")

    st.header("What is our goal?")
    st.write("Our project goal is to inform and give relief to people who are still deliberating on whether they should get a COVID-19 vaccine. We aim to provide objective facts and figures regarding COVID-19 vaccine side effects in a way that is both easy to understand and tailored to each individual user.")

    if st.button("Let's get started!"):
        state.navigation = "Inputs"


# Only used if this file is ran directly
# Useful for developing with hot reloading
if __name__ == "__main__":
    from session import _get_state
    main(_get_state())
