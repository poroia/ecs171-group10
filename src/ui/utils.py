import streamlit as st


def sidebar_width_slider(state):
    sidebar_width = state.settings['sidebar_width'][state.navigation]

    state.settings['sidebar_width'][state.navigation] = st.slider(
        f"Sidebar Width for {state.navigation} page", 300, 500, 
        sidebar_width)

    st.markdown(
        f'''
        <style>
            [data-testid="stSidebar"] > div:first-child {{
                width: {sidebar_width}px;
                padding-left: 2em;
                padding-right: 2em;
            }}

            [data-testid="stSidebar"][aria-expanded="false"] > div:first-child
            {{
                margin-left: -{sidebar_width}px;
            }}
        </style>
        ''',
        unsafe_allow_html=True,
    )


def main_debug_helper(state):
    with st.sidebar:
        st.markdown("***")
        st.title("Settings")
        sidebar_width_slider(state)
