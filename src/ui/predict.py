from typing import Union
import threading
import av
import numpy as np
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, ClientSettings, webrtc_streamer

def main(state):
    class VideoProcessor(VideoProcessorBase):
        frame_lock: threading.Lock  # `recv()` is running in another thread,
        # then a lock object is used here for thread-safety.
        out_image: Union[np.ndarray, None]

        def __init__(self) -> None:
            self.frame_lock = threading.Lock()
            self.out_image = None

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            in_image = frame.to_ndarray(format="bgr24")
            out_image = in_image[:, ::-1, :]  # flip horizontal

            with self.frame_lock:
                self.out_image = out_image
                
            return av.VideoFrame.from_ndarray(out_image, format="bgr24")

    ctx = webrtc_streamer(
        key = "snapshot", 
        client_settings = ClientSettings(
            media_stream_constraints = {"video": True, "audio": False},
        ),
        video_processor_factory = VideoProcessor
    )

    if ctx.video_processor:
        if st.button("Snapshot"):
            with ctx.video_processor.frame_lock:
                out_image = ctx.video_processor.out_image

            if out_image is not None:
                st.write("Output image:")
                st.image(out_image, channels="BGR")
            else:
                st.warning("No frames available yet.")
