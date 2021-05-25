import numpy as np
import streamlit as st
import threading
from av import VideoFrame
from typing import Optional
from PIL import Image as PILImage
from streamlit_webrtc import VideoProcessorBase, ClientSettings, webrtc_streamer
from streamlit_image_crop import image_crop, Crop

PICTURE_DEFAULT_SRC = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" >'
    '<g fill="none" stroke="gray" stroke-width="3" stroke-linecap="round">'
    '<ellipse cx="50" cy="40" rx="19" ry="18" />'
    '<path d="M34.103 60.963C26.318 63.22 18.595 72.53 17.66 81.957M65.705 61.113c7.785 2.258 15.508 11.57 16.443 20.995" />'
    "</g>"
    "</svg>"
)


def main(state):

    st.title("Inputs")

    inputs_form(state)


def inputs_form(state):
    picture_input(state)

    first_col, second_col = st.beta_columns((1, 1))
    
    with first_col:
        vax_manu: str
        vax_manu = st.radio(
            "Which vaccine did you get?", ("Pfizer\BioNTech", "Moderna", "J&J\Janssen"))
        if vax_manu == 'J&J\Janssen':
            vax_manu = 'Janssen'
        state.inputs['vax_manu'] = vax_manu.upper()
    
    with second_col:
        state.inputs['vax_dose_series'] = st.radio("Which dose have you gotten so far?", (1, 2))

    if st.button("See results!"):
        state.navigation = "Results"


def picture_input(state):
    picture_area: st = None

    cropper_col, capture_col = st.beta_columns((1, 1.5))

    with cropper_col:
        picture_area = st.empty()
        if state.inputs_config["picture_raw"]:
            st.write("Please crop the picture so that your face fits perfectly in the frame.")

            cropped_image = image_crop(
                state.inputs_config["picture_raw"],
                key="ecs171-group10",
                crop=Crop(aspect=1.0),
            )

            if cropped_image:
                state.inputs["picture"] = cropped_image.resize((48, 48))
                state.inputs_config["cropper_cropped_once"] = True
                st.image(state.inputs["picture"])  # debugging

            elif not state.inputs_config["cropper_cropped_once"] \
                and state.inputs["picture"] is None:
                st.warning(
                    ":warning: Don't forget to crop your picture!"
                )

            elif state.inputs_config["cropper_cropped_once"] \
                and state.inputs["picture"] is None:
                st.error(
                    ":no_entry: Make sure you have a selection box around your face!"
                )

        else:
            picture_area.write(
                PICTURE_DEFAULT_SRC,
                unsafe_allow_html=True,
            )

    with capture_col:
        option = st.selectbox("Select Capture Method", ("Webcam", "Upload Picture"))
        if option == "Webcam":
            webcam(state)
        elif option == "Upload Picture":
            file_uploader(state)


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


# Only used if this file is ran directly
# Useful for developing with hot reloading
if __name__ == "__main__":
    from session import _get_state

    main(_get_state())
