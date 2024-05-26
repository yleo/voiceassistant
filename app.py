import streamlit as st
from audio_recorder_streamlit import audio_recorder
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile

# Initialize session state
if "recording" not in st.session_state:
    st.session_state["recording"] = False
if "audio_bytes" not in st.session_state:
    st.session_state["audio_bytes"] = None

def start_recording():
    st.session_state["recording"] = True
    st.session_state["audio_bytes"] = audio_recorder()

def stop_recording():
    st.session_state["recording"] = False

# Streamlit app
st.title("Voice Recorder")

if st.session_state["recording"]:
    stop_button = st.button("Stop")
    if stop_button:
        stop_recording()
else:
    record_button = st.button("Record")
    if record_button:
        start_recording()

# Display the audio player if a recording exists
if st.session_state["audio_bytes"]:
    st.audio(st.session_state["audio_bytes"], format="audio/wav")

    # Save the recording to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(temp_file.name, "wb") as f:
        f.write(st.session_state["audio_bytes"])

    st.success(f"Recording saved to {temp_file.name}")

st.caption("Click 'Record' to start recording and 'Stop' to save your recording.")
