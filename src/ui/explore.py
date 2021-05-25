import numpy as np
import streamlit as st

from ui import utils


def main(state):

    st.title("Explore")


# Only used if this file is ran directly
# Useful for developing with hot reloading
if __name__ == "__main__":
    from session import _get_state
    state = _get_state()
    state.navigation = 'Explore'

    main(state)

    utils.main_debug_helper(state)
