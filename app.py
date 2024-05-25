import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import pydub
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile

# Define client settings
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"audio": True, "video": False},
)

# Function to save audio to a WAV file
def save_wav(filename, data, fs):
    wavfile.write(filename, fs, data)

# Streamlit app
st.title("Voice Recorder")
webrtc_ctx = webrtc_streamer(key="example", mode=WebRtcMode.SENDRECV, client_settings=WEBRTC_CLIENT_SETTINGS)

if st.button("Record"):
    if webrtc_ctx.audio_receiver:
        audio_frames = webrtc_ctx.audio_receiver.get_frames()
        if audio_frames:
            audio = pydub.AudioSegment(
                data=b"".join([frame.to_ndarray().tobytes() for frame in audio_frames]),
                sample_width=2,
                frame_rate=44100,
                channels=1
            )

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            audio.export(temp_file.name, format="wav")

            st.audio(temp_file.name)
            st.success(f"Recording saved to {temp_file.name}")
        else:
            st.warning("No audio frames received")
    else:
        st.warning("Audio receiver is not set up")
