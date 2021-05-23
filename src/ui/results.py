import streamlit as st


def main(state):
    st.title(":chart_with_upwards_trend: Results!")


# Only used if this file is ran directly
# Useful for developing with hot reloading
if __name__ == "__main__":
    from session import _get_state
    main(_get_state())
