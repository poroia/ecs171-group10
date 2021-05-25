import os
import threading
import joblib
import streamlit as st
import numpy as np
import pandas as pd
from typing import Callable, Tuple, Optional
from tensorflow import keras
from PIL import Image as PILImage
from av import VideoFrame
from streamlit_webrtc import VideoProcessorBase, ClientSettings, \
    webrtc_streamer
from streamlit_image_crop import image_crop, Crop

from ui import utils

# correctly establishes base path if you run app.py
# or this script for debugging purposes 
ROOT_RELATIVE_PATH = "./"
# debug
DEBUG = False


def main(state):
    with st.sidebar:
        inputs(state)

        if DEBUG:
            debug(state)
    
    results(state)


# ===============================================
# INPUTS
# ===============================================


PICTURE_DEFAULT_SRC = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" >'
    '<g fill="none" stroke="gray" stroke-width="3" stroke-linecap="round">'
    '<ellipse cx="50" cy="40" rx="19" ry="18" />'
    '<path d="M34.103 60.963C26.318 63.22 18.595 72.53 17.66 81.957M65.705 \
        61.113c7.785 2.258 15.508 11.57 16.443 20.995" />'
    "</g>"
    "</svg>"
)


def inputs(state):
    st.title("Inputs")

    st.write("####") # spacer
    picture_input(state)

    st.write("###") # spacer
    vax_manu = st.radio(
        "Which vaccine would you like to test?",
        ("Pfizer\BioNTech", "Moderna", "J&J\Janssen"))
    vax_manu = 'Janssen' if vax_manu == 'J&J\Janssen' else vax_manu
    state.inputs['vax_manu'] = vax_manu.upper()

    st.write("####") # spacer
    state.inputs['vax_dose_series'] = st.radio(
        "Which dose count would you like to test?", (1, 2))

    st.write("####") # spacer
    st.write("And that's all!")


def picture_input(state):

    option = st.selectbox(
        "Select Capture Method", ("Webcam", "Upload Picture"))
    if option == "Webcam":
        webcam(state)
    elif option == "Upload Picture":
        file_uploader(state)
    
    
    if state.inputs_config["picture_raw"]:
        st.write("####")

        note = st.empty()

        _, picture_col, _ = st.beta_columns((1, 3, 1))

        with picture_col:
            cropped_image = image_crop(
                state.inputs_config["picture_raw"],
                key="ecs171-group10",
                crop=Crop(aspect=1.0),
            )

        if cropped_image:
            state.inputs["picture"] = cropped_image.resize((48, 48))
            state.inputs_config["cropper_cropped_once"] = True
            note.success(":white_check_mark: Picture saved!")

        elif state.inputs["picture"] is None:
            note.warning(
                ":warning: Please crop the picture so that your face fits \
                    perfectly in the frame."
            )
        
        elif cropped_image is None:
            note.info(
                ":information_source: No crop was found, but using last crop \
                    done."
            )

        

def webcam(state):
    class VideoProcessor(VideoProcessorBase):
        frame_lock: threading.Lock  # `recv()` is running in another thread,
        # then a lock object is used here for thread-safety.
        out_image: Optional[PILImage.Image]

        def __init__(self) -> None:
            self.frame_lock = threading.Lock()
            self.out_image = None

        def recv(self, frame: VideoFrame) -> VideoFrame:
            in_image = frame.to_image()
            out_image = in_image.transpose(PILImage.FLIP_LEFT_RIGHT)

            with self.frame_lock:
                self.out_image = out_image

            return VideoFrame.from_image(out_image)

    ctx = webrtc_streamer(
        key="ecs171-group10",
        client_settings=ClientSettings(
            media_stream_constraints={"video": True, "audio": False},
        ),
        video_processor_factory=VideoProcessor,
    )

    if ctx.video_processor:
        if st.button("Take a picture"):
            with ctx.video_processor.frame_lock:
                out_image = ctx.video_processor.out_image

            if out_image is not None:
                state.inputs_config["picture_raw"] = out_image

            else:
                st.warning("No frames available yet.")


def file_uploader(state):
    file_buffer = st.file_uploader("", type=["png", "jpg", "jpeg"])

    if file_buffer is not None:
        out_image = PILImage.open(file_buffer)
        state.inputs_config["picture_raw"] = out_image


# ===============================================
# RESULTS
# ===============================================


def results(state):
    st.title(":chart_with_upwards_trend: Predict!")

    if state.inputs["picture"] is not None:
        sex_raw, age_range_raw = predict_picture(state)
        state.inputs['sex'] = sex_raw
        state.inputs['age_range'] = age_range_raw
        

    if state.inputs['age_range'] is not None \
        and state.inputs['sex'] is not None \
        and state.inputs['vax_manu'] is not None \
        and state.inputs['vax_dose_series'] is not None:

        
        results_symptoms_raw = predict_symptoms(
            state.inputs['age_range'],
            state.inputs['sex'],
            state.inputs['vax_manu'],
            state.inputs['vax_dose_series']
        )
        results_outcomes_raw = predict_outcomes(
            state.inputs['age_range'],
            state.inputs['sex'],
            state.inputs['vax_manu'],
            state.inputs['vax_dose_series']
        )

        # preprocess
        sex = "male" if sex_raw == 'M' else 'female'
        age_start, age_end = age_range_raw

        results_symptoms = dict(sorted(
            results_symptoms_raw.copy().items(), 
            key=lambda x: x[1], reverse=True))
        for name, rate in results_symptoms.items():
            results_symptoms[name] = "{:.2%}".format(rate)
        df_symptoms = pd.DataFrame(np.transpose([
            list(results_symptoms.keys()),
            list(results_symptoms.values())]), columns=['symptoms', 'percentage'])

        results_outcomes = {}
        results_outcomes['Death'] = results_outcomes_raw['DIED']
        results_outcomes['Disabled'] = results_outcomes_raw['DISABLE']
        results_outcomes['Hospitalized'] = results_outcomes_raw['HOSPITAL']
        results_outcomes['Life threatening'] = results_outcomes_raw['L_THREAT']
        results_outcomes['Recovered'] = results_outcomes_raw['RECOVD']
        for name, rate in results_outcomes.items():
            results_outcomes[name] = "{:.2%}".format(rate)
        df_outcomes = pd.DataFrame(np.transpose([
            list(results_outcomes.keys()),
            list(results_outcomes.values())]), columns=['outcome', 'percentage'])
        
        # style (attempt)
        st.markdown(
            """
            <style>
                .css-1l40rdr, .css-1s64co1 { text-align: left }
            </style>
            """, unsafe_allow_html=True) 

        # content
        st.markdown("#####") # spacer

        st.header("Demographic")
        st.write(f"We predicted that you were a *{sex}* with \
            an age range from *{age_start}* to *{age_end}*.")

        st.write("***")
        st.header("Symptoms")
        st.write("People like you were most likely to experience these \
            symptoms after taking the vaccine at the specified dose:")
        
        for name, percentage in list(results_symptoms.items())[:10]:
            st.write(f"- **{name}**: {percentage}")

        st.write("###") # spacer
        with st.beta_expander("See a full list"):
            st.dataframe(df_symptoms)

        st.write("***")
        st.header("Outcomes")
        st.write("What ended up happening? Here are a list of chances that \
            certain outcomes can occur if you got the virus after getting the \
                vaccine:")
        for name, percentage in list(results_outcomes.items()):
            st.write(f"- **{name}**: {percentage}")
        

        # bars = alt.Chart(df_outcomes).mark_bar().encode(
        #     x='percentage:Q',
        #     y='outcome:O'
        # )
        # text = bars.mark_text(
        #     align='left',
        #     baseline='middle',
        #     dx=3,  # Nudges text to right so it doesn't appear on top of the bar
        #     color="white"
        # ).encode(
        #     text='percentage:Q'
        # )
        # st.altair_chart((bars + text).properties(height=300))
    
    else:
        st.write("###")
        st.info("Start by filling out your information on the sidebar!")


def predict_picture(state):
    # get picture
    picture = state.inputs["picture"]
    # convert to grayscale
    picture_grayscale = picture.convert("LA")
    # convert to array
    picture_grayscale_array = np.array(picture_grayscale)
    # change innermost array to only get grayscale value
    # picture_grayscale_array[::, ::, [0]]
    processed_picture = np.array(
        [[[g[0] / 255] for g in r] for r in picture_grayscale_array])

    return (predict_sex(processed_picture), predict_age(processed_picture))


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
    age_range = (
        age_bins[age_result_bins_index], age_bins[age_result_bins_index + 1])
    return age_range


@st.cache
def predict_symptoms(age_yrs_range, sex, vax_manu, vax_dose_series) -> dict:
    SYMPTOMS_BASE_PATH = os.path.join(
        ROOT_RELATIVE_PATH, "./src/models/symptoms-sklearn/")

    # load models into dicts    
    encoders = load_models(SYMPTOMS_BASE_PATH, "encoder_")
    models = load_models(
        SYMPTOMS_BASE_PATH, "model_",
        transform_names=lambda x: x.replace("_", " ").capitalize())
    models_rates = dict.fromkeys(models.copy().keys(), 0)

    age_yrs_values = get_age_yrs_values(age_yrs_range)
    # iterate using all selected values in age range
    for i, age_yrs in enumerate(age_yrs_values):
        processed_input = [
            age_yrs,
            encoders['SEX'].transform([sex])[0],
            encoders['VAX_MANU'].transform([vax_manu])[0],
            vax_dose_series
        ]

        # predict and set new running mean for each model
        for name, model in models.items():
            new_rate = model.predict_proba([processed_input]).tolist()[0][1]
            running_mean_rate = models_rates[name]
            models_rates[name] = ((running_mean_rate * i) + new_rate) / (i + 1)

    return models_rates


@st.cache
def predict_outcomes(age_yrs_range, sex, vax_manu, vax_dose_series):
    OUTCOMES_BASE_PATH = os.path.join(
        ROOT_RELATIVE_PATH, "./src/models/outcomes-sklearn/")
    
    # load models into dicts    
    scalers = load_models(OUTCOMES_BASE_PATH, "scaler_")
    encoders = load_models(OUTCOMES_BASE_PATH, "encoder_")
    models = load_models(OUTCOMES_BASE_PATH, "model_")
    models_rates = dict.fromkeys(models.copy().keys(), 0)

    age_yrs_values = get_age_yrs_values(age_yrs_range)
    # iterate using all selected values in age range
    for i, age_yrs in enumerate(age_yrs_values):
        processed_input = [
            scalers['AGE_YRS'].transform([[age_yrs]])[0][0],
            encoders['SEX'].transform([sex])[0],
            encoders['VAX_MANU'].transform([vax_manu])[0],
            vax_dose_series
        ]

        # predict and set new running mean for each model
        for name, model in models.items():
            # decode transform on the original data in index_yes
            index_yes = \
                0 if encoders[name].inverse_transform([0]) == ['Y'] else 1
            new_rate = \
                model.predict_proba([processed_input]).tolist()[0][index_yes]
            running_mean_rate = models_rates[name]
            models_rates[name] = ((running_mean_rate * i) + new_rate) / (i + 1)

    return models_rates
    

def load_models(base_path, prefix, extension='.pkl',
    transform_names:Callable[[str], str]=lambda x: x) -> dict:
    
    files = list(filter(
        lambda filename: filename.startswith(prefix), os.listdir(base_path)))
    models = list(map(
        lambda filename: \
            joblib.load(os.path.join(base_path, filename)), files))
    model_names = list(map(
        lambda filename: \
            transform_names(filename[len(prefix):-len(extension)]), files))
    
    results = {}
    for i, model_name in enumerate(model_names):
        model = models[i]
        results[model_name] = model

    return results


def get_age_yrs_values(age_yrs_range: Tuple[int, int]):
    MAX_ITERATIONS = 6
    age_yrs_range = (
        age_yrs_range[0], age_yrs_range[1] + 1) # make end inclusive
    age_yrs_values = [l[0] for l in np.array_split(
        range(*age_yrs_range), MAX_ITERATIONS) if len(l)]
    return age_yrs_values


def debug(state):
    st.title("Debug")
    with st.beta_expander("Debug"):
        first_col, second_col = st.beta_columns((1, 1))

        with first_col:
            if st.button("Fill Inputs"):
                state.inputs["picture"] = PILImage.open(
                    os.path.join(ROOT_RELATIVE_PATH, 
                    "./prototype/data/sample-cropped.jpeg"))
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
    print("I WAS HERE LOL")
    from session import _get_state
    state = _get_state()
    state.navigation = 'Predict'

    main(state)

    utils.main_debug_helper(state)
