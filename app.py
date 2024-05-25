import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import pydub
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile

# Define client settings for WebRTC
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

if "audio_buffer" not in st.session_state:
    st.session_state["audio_buffer"] = []

def recorder_callback(frame: av.AudioFrame):
    audio = frame.to_ndarray()
    st.session_state["audio_buffer"].append(audio)
    return av.AudioFrame.from_ndarray(audio, format="s16")

webrtc_ctx.audio_receiver.on_frame = recorder_callback

if st.button("Stop and Save Recording"):
    if len(st.session_state["audio_buffer"]) > 0:
        # Concatenate all audio chunks
        audio_data = np.concatenate(st.session_state["audio_buffer"], axis=0)
        st.session_state["audio_buffer"] = []  # Clear the buffer

        # Save the recording to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        save_wav(temp_file.name, audio_data, 44100)

        st.audio(temp_file.name, format='audio/wav')
        st.success(f"Recording saved to {temp_file.name}")
    else:
        st.warning("No audio recorded yettt")

st.caption("Click 'Stop and Save Recording' to save your recording.")
