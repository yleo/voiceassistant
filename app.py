import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings, AudioProcessorBase
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile

# Define client settings for WebRTC
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"audio": True, "video": False},
)

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.audio_buffer.append(audio)
        return frame

# Streamlit app
st.title("Voice Recorder")

# Initialize session state
if "webrtc_ctx" not in st.session_state:
    st.session_state["webrtc_ctx"] = None
if "recording" not in st.session_state:
    st.session_state["recording"] = False
if "audio_file" not in st.session_state:
    st.session_state["audio_file"] = None

# Function to start recording
def start_recording():
    st.session_state["webrtc_ctx"] = webrtc_streamer(
        key="example", 
        mode=WebRtcMode.SENDONLY,
        client_settings=WEBRTC_CLIENT_SETTINGS, 
        audio_processor_factory=AudioProcessor
    )
    st.session_state["recording"] = True
    st.session_state["audio_file"] = None
    st.experimental_rerun()

# Function to stop recording and save the file
def stop_recording():
    if st.session_state["webrtc_ctx"] and st.session_state["webrtc_ctx"].state.playing:
        audio_processor = st.session_state["webrtc_ctx"].audio_processor
        if audio_processor and len(audio_processor.audio_buffer) > 0:
            audio_data = np.concatenate(audio_processor.audio_buffer, axis=0)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            wavfile.write(temp_file.name, 44100, audio_data)

            st.session_state["audio_file"] = temp_file.name
            st.success(f"Recording saved to {temp_file.name}")

            audio_processor.audio_buffer = []
        else:
            st.warning("No audio recorded yet")
        
        st.session_state["webrtc_ctx"].stop()
        st.session_state["recording"] = False
        st.experimental_rerun()
    else:
        st.warning("Recording has not started or already stopped.")

# Display buttons and handle actions
if st.session_state["recording"]:
    if st.button("Stop"):
        stop_recording()
else:
    if st.button("Record"):
        start_recording()

# Display the audio player if a file is available
if st.session_state["audio_file"]:
    st.audio(st.session_state["audio_file"], format='audio/wav')

st.caption("Click 'Record' to start recording and 'Stop' to save your recording.")
