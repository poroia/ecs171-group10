import numpy as np
import streamlit as st

from ui import welcome, predict

state = {
    "navigation": None,
    "test": 5
}

PAGES = {
    "Welcome": welcome.main,
    "Predict": predict.main,
}


def main():
    st.sidebar.title("Navigation")
    state["navigation"] = st.sidebar.radio("", list(PAGES.keys()))
    PAGES[state["navigation"]](state)


if __name__ == "__main__":
    main()
