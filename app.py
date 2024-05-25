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
webrtc_ctx = webrtc_streamer(
    key="example", 
    mode=WebRtcMode.SENDRECV, 
    client_settings=WEBRTC_CLIENT_SETTINGS, 
    audio_processor_factory=AudioProcessor
)

if st.button("Stop and Save Recording"):
    if webrtc_ctx.state.playing:
        audio_processor = webrtc_ctx.audio_processor
        if audio_processor and len(audio_processor.audio_buffer) > 0:
            # Concatenate all audio chunks
            audio_data = np.concatenate(audio_processor.audio_buffer, axis=0)
            audio_processor.audio_buffer = []  # Clear the buffer

            # Save the recording to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            wavfile.write(temp_file.name, 44100, audio_data)

            st.audio(temp_file.name, format='audio/wav')
            st.success(f"Recording saved to {temp_file.name}")
        else:
            st.warning("No audio recorded yet")
    else:
        st.warning("WebRTC is not playing")

st.caption("Click 'Stop and Save Recording' to save your recording.")
