import os
import joblib
import streamlit as st
import numpy as np
from tensorflow import keras
from PIL import Image as PILImage

# correctly establishes base path if you run app.py
# or this script for debugging purposes 
ROOT_RELATIVE_PATH = "./"

def main(state):
    st.title(":chart_with_upwards_trend: Results!")

    debug(state)

    if state.inputs["picture"]:
        predict_picture(state)
    
    if state.inputs['age_range'] is not None \
        and state.inputs['sex'] is not None \
        and state.inputs['vax_manu'] is not None \
        and state.inputs['vax_dose_series'] is not None:

        results = predict_symptoms(
            state.inputs['age_range'],
            state.inputs['sex'],
            state.inputs['vax_manu'],
            state.inputs['vax_dose_series']
        )
        st.write(results)

        # predict_outcomes(
        #     state.inputs['age_range'],
        #     state.inputs['sex'],
        #     state.inputs['vax_manu'],
        #     state.inputs['vax_dose_series']
        # )

def predict_picture(state):
    # get picture
    picture = state.inputs["picture"]
    # convert to grayscale
    picture_grayscale = picture.convert("LA")
    # convert to array
    picture_grayscale_array = np.array(picture_grayscale)
    # change innermost array to only get grayscale value
    processed_picture = np.array([[[g[0] / 255] for g in r] for r in picture_grayscale_array])

    state.inputs['sex'] = predict_sex(processed_picture)
    state.inputs['age_range'] = predict_age(processed_picture)


@st.cache
def predict_sex(processed_picture) -> str:
    sex_model = keras.models.load_model(
        os.path.join(ROOT_RELATIVE_PATH, "./src/models/sex-keras"))
    sex_result = sex_model.predict(np.array([processed_picture]))
    sex = np.argmax(sex_result)
    return 'M' if int(sex) == 0 else 'F'


@st.cache
def predict_age(processed_picture) -> tuple:
    age_bins = (0, 12, 15, 18, 28, 40, 50, 65, 80, 100, 200)

    age_model = keras.models.load_model(
        os.path.join(ROOT_RELATIVE_PATH, "./src/models/age-keras"))
    age_result = age_model.predict(np.array([processed_picture]))
    age_result_bins_index = np.argmax(age_result)
    age_range = (age_bins[age_result_bins_index], age_bins[age_result_bins_index + 1])
    return age_range


@st.cache
def predict_symptoms(age_yrs_range, sex, vax_manu, vax_dose_series) -> dict:
    SYMPTOMS_BASE_PATH = os.path.join(
        ROOT_RELATIVE_PATH, "./src/models/symptoms-sklearn/")
    
    encoder_VAX_MANU = joblib.load(os.path.join(SYMPTOMS_BASE_PATH, "encoder_VAX_MANU.pkl"))
    encoder_SEX = joblib.load(os.path.join(SYMPTOMS_BASE_PATH, "encoder_SEX.pkl"))

    processed_input = [
        age_yrs_range[0],
        encoder_SEX.transform([sex]),
        encoder_VAX_MANU.transform([vax_manu]),
        vax_dose_series
    ]
    
    models_info = load_models(SYMPTOMS_BASE_PATH, "symptoms_")
    for name, model in models_info.items():
        models_info[name] = model.predict_proba([processed_input]).tolist()[0][1]
    
    return models_info


@st.cache
def predict_outcomes(age_yrs_range, sex, vax_manu, vax_dose_series):
    
    OUTCOMES_BASE_PATH = os.path.join(
        ROOT_RELATIVE_PATH, "./src/models/outcomes-sklearn/")
    outcomes_model = joblib.load(os.path.join(OUTCOMES_BASE_PATH, "outcomes.pkl"))
    scaler_AGE_YRS = joblib.load(os.path.join(OUTCOMES_BASE_PATH, "scaler_AGE_YRS.pkl"))
    encoder_VAX_MANU = joblib.load(os.path.join(OUTCOMES_BASE_PATH, "encoder_VAX_MANU.pkl"))
    encoder_SEX = joblib.load(os.path.join(OUTCOMES_BASE_PATH, "encoder_SEX.pkl"))
    print(scaler_AGE_YRS.transform([[age_yrs_range[0]]]))
    print(encoder_VAX_MANU.transform([vax_manu]))
    print(encoder_SEX.transform([sex]))
    

def load_models(base_path, prefix) -> dict:
    files = list(
        filter(lambda filename: filename.startswith(prefix), os.listdir(base_path)))
    models = list(
        map(lambda filename: joblib.load(os.path.join(base_path, filename)), files))
    model_names = list(
        map(lambda filename: filename[9:-4].replace("_", " ").title(), files))
    
    results = {}
    for i, model_name in enumerate(model_names):
        model = models[i]
        results[model_name] = model

    return results


def debug(state):
    with st.beta_expander("Debug"):
        first_col, second_col = st.beta_columns((1, 4))

        with first_col:
            if st.button("Fill Inputs"):
                state.inputs["picture"] = PILImage.open(
                    os.path.join(ROOT_RELATIVE_PATH, "./prototype/data/sample-cropped.jpeg"))
                state.inputs['vax_manu'] = 'MODERNA'
                state.inputs['vax_dose_series'] = 2
        
        with second_col:
            if st.button("⟳"):
                pass
        
        st.write(state.inputs)


# Only used if this file is ran directly
# Useful for developing with hot reloading
if __name__ == "__main__":
    ROOT_RELATIVE_PATH = "../"
    from session import _get_state
    main(_get_state())
