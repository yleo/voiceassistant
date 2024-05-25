import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile

# Function to record audio
def record_audio(duration, fs=44100):
    st.info(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    return recording

# Function to save audio to a WAV file
def save_wav(filename, data, fs):
    wavfile.write(filename, fs, data)

# Streamlit app
st.title("Voice Recorder")
duration = st.slider("Select recording duration (seconds)", min_value=1, max_value=10, value=5)
record_button = st.button("Record")

if record_button:
    audio_data = record_audio(duration)
    st.audio(audio_data, format='audio/wav')
    
    # Save the recording to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    save_wav(temp_file.name, audio_data, 44100)
    
    st.success(f"Recording saved to {temp_file.name}")
