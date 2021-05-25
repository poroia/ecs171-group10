import streamlit as st
from ui import welcome, predict, explore, utils, session


def main(state: session._SessionState):
    pages = {
        "Welcome": welcome.main,
        "Predict": predict.main,
        "Explore": explore.main,
    }     

    with st.sidebar:
        st.title("Navigation")

        navigation_index = list(pages.keys()).index(state.navigation or "Welcome")
        state.navigation = st.radio(
            "", list(pages.keys()), index=navigation_index)
        

    pages[state.navigation](state)

    with st.sidebar:
        st.markdown("***")
        st.title("Settings")
        utils.sidebar_width_slider(state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


if __name__ == "__main__":
    main(session._get_state())
