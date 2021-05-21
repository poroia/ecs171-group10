import numpy as np
import streamlit as st
import threading
from av import VideoFrame
from typing import Optional
from PIL import Image as PILImage
from streamlit_webrtc import VideoProcessorBase, ClientSettings, webrtc_streamer

PICTURE_DEFAULT_SRC = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="162">'
    '<g fill="none" stroke="gray" stroke-width="3" stroke-linecap="round">'
    '<ellipse cx="50" cy="40" rx="19" ry="18" />'
    '<path d="M34.103 60.963C26.318 63.22 18.595 72.53 17.66 81.957M65.705 61.113c7.785 2.258 15.508 11.57 16.443 20.995" />'
    "</g>"
    "</svg>"
)


def main(state):
    picture_area: st

    st.title(":chart_with_upwards_trend: Predict")

    inputs_expander = st.beta_expander("Inputs", expanded=state.inputs_expanded)
    with inputs_expander:

        image_col, set_col = st.beta_columns([1, 3])
        with image_col:
            picture_area = st.empty()
            if state.inputs['picture'] is not None:
                picture_area.image(state.inputs['picture'], channels="BGR")
            else:
                picture_area.write(
                    PICTURE_DEFAULT_SRC,
                    unsafe_allow_html=True,
                )

        with set_col:
            option = st.selectbox(
                "Select Capture Method", ("Webcam", "Upload Picture")
            )
            if option == "Webcam":
                webcam(state, picture_area)
            elif option == "Upload Picture":
                file_uploader(state, picture_area)

        if st.button("Submit"):
            state.inputs_expanded = False

    # with st.form("input"):
    # st.header("YEET")
    # if st.form_submit_button("Submit"):


def webcam(state, picture_area):
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
        key="snapshot",
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
                picture_area.image(out_image)
                state.inputs["picture"] = out_image

            else:
                st.warning("No frames available yet.")

def file_uploader(state, picture_area):
    uploaded_file = st.file_uploader("", type="jpg")

    if uploaded_file is not None:
        # To read file as bytes:
        out_image = uploaded_file.getvalue()
        state.inputs["picture"] = out_image
        picture_area.image(out_image)

        # # To convert to a string based IO:
        # stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        # st.write(stringio)

        # # To read file as string:
        # string_data = stringio.read()
        # st.write(string_data)

        # # Can be used wherever a "file-like" object is accepted:
        # dataframe = pd.read_csv(uploaded_file)
        # st.write(dataframe)

# Only used if this file is ran directly
# Useful for developing with hot reloading
if __name__ == "__main__":
    from session import _get_state
    main(_get_state())
