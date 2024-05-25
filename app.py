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
        return frame  # Return the frame to ensure it's processed but not played back

# Streamlit app
st.title("Voice Recorder")

# Initialize session state
if "webrtc_ctx" not in st.session_state:
    st.session_state["webrtc_ctx"] = None
if "recording" not in st.session_state:
    st.session_state["recording"] = False

# Function to start recording
def start_recording():
    st.session_state["webrtc_ctx"] = webrtc_streamer(
        key="example", 
        mode=WebRtcMode.SENDONLY,  # Change mode to SENDONLY to avoid playback
        client_settings=WEBRTC_CLIENT_SETTINGS, 
        audio_processor_factory=AudioProcessor
    )
    st.session_state["recording"] = True

# Function to stop recording and save the file
def stop_recording():
    if st.session_state["webrtc_ctx"] and st.session_state["webrtc_ctx"].state.playing:
        audio_processor = st.session_state["webrtc_ctx"].audio_processor
        if audio_processor and len(audio_processor.audio_buffer) > 0:
            # Concatenate all audio chunks
            audio_data = np.concatenate(audio_processor.audio_buffer, axis=0)
            
            # Save the recording to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            wavfile.write(temp_file.name, 44100, audio_data)

            st.audio(temp_file.name, format='audio/wav')
            st.success(f"Recording saved to {temp_file.name}")
            
            # Clear the buffer after saving
            audio_processor.audio_buffer = []
        else:
            st.warning("No audio recorded yet")
        st.session_state["webrtc_ctx"].stop()
        st.session_state["recording"] = False
    else:
        st.warning("Recording has not started or already stopped.")

# Display buttons and handle actions
if not st.session_state["recording"]:
    if st.button("Record"):
        start_recording()
else:
    if st.button("Stop"):
        stop_recording()

st.caption("Click 'Record' to start recording and 'Stop' to save your recording.")
