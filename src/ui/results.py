import streamlit as st
from tensorflow import keras
import joblib


def main(state):
    st.title(":chart_with_upwards_trend: Results!")

    load_model(state)

def load_model(state):
    gender_model = keras.models.load_model("./models/gender-keras")
    st.text(gender_model)
    
    age_model = keras.models.load_model("./models/age-keras")
    st.text(age_model)

    symptoms_model = joblib.load("./models/symptoms.pkl")
    st.text(symptoms_model)

    outcomes_model = joblib.load("./models/outcomes.pkl")
    st.text(outcomes_model)

# Only used if this file is ran directly
# Useful for developing with hot reloading
if __name__ == "__main__":
    from session import _get_state
    main(_get_state())
