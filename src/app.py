import streamlit as st
from collections import OrderedDict
from ui import welcome, predict, session


# state = {
#    "navigation": None, # current page name
#    "inputs": {
#        "picture": PIL.Image | None,
#    },
# }
def main(state: session._SessionState):
    pages = OrderedDict(
        (
            ("Welcome", welcome.main),
            ("Predict", predict.main),
        )
    )

    st.sidebar.title("Navigation")

    navigation_index = list(pages.keys()).index(state.navigation or "Welcome")
    state.navigation = st.sidebar.radio(
        "", list(pages.keys()), index=navigation_index)

    pages[state.navigation](state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


if __name__ == "__main__":
    main(session._get_state())
