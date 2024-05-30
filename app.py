import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests
import tempfile
import json
import numpy as np
import wave
import io
import subprocess
from groq import Groq

# Global Variables for API Endpoints and Tokens
HUGGING_FACE_API_ENDPOINT = "https://ih8dpnlow2junbl4.us-east-1.aws.endpoints.huggingface.cloud"
LLM_API_KEY = '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'
HUGGING_FACE_AUDIO_ENDPOINT = "https://yh2m49z3xrn07uzh.us-east-1.aws.endpoints.huggingface.cloud"
HUGGING_FACE_API_TOKEN = "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"

# Function to send audio file to Hugging Face API
def send_to_hugging_face_api(file_path):
    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}",
        "Content-Type": "audio/wav"
    }
    with open(file_path, "rb") as f:
        data = f.read()
        response = requests.post(HUGGING_FACE_API_ENDPOINT, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to get a valid response: {response.status_code}, {response.text}"}

# Function to process the audio and send it to the API
def process_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name
    
    st.audio(audio_bytes, format="audio/wav")
    
    with st.spinner("Sending audio to API..."):
        result = send_to_hugging_face_api(temp_file_path)
    
    return result

# Function to interact with LLM
def get_llm_response(query_text):
    client = Groq(api_key=LLM_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Répondez à cette question en moins de 20 mots en tant que gentil assistant vocal. La question:  {query_text}",
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Function to generate audio response
def generate_audio_response(answer):

    # Define the local paths for the model and configuration files
    model_path = "fr_FR_upmc_medium.onnx"
    config_path = "fr_FR_upmc_medium.onnx.json"
    output_file = "output.wav"

    # Run Piper-TTS using subprocess with local model and config files
    process = subprocess.Popen([
        "piper",
        "--model", model_path,
        "--config", config_path,
        "--output_file", output_file
    ], stdin=subprocess.PIPE, text=True)

    # Pass the text to Piper through stdin
    process.communicate(input=answer)

    print(f"Speech synthesis complete. Output saved to {output_file}")

    # Read the generated WAV file into a byte stream
    with open(output_file, "rb") as f:
        audio_data = f.read()

    return audio_data

# Main function
def main():
    st.title("Voice Recorder 8")
    audio_bytes = audio_recorder()
    result = ""

    if audio_bytes:
        result = process_audio(audio_bytes)
        st.write("API Response:", result)
        
        if 'text' in result:
            answer = get_llm_response(result['text'])
            st.write("LLM Response:", answer)
            
            audio_data = generate_audio_response(answer)

            if audio_data:
                st.title("Audio Playback in Streamlit")
                st.write("Generated Audio:")
                st.audio(audio_data, format='audio/wav')
            else:
                st.error("Failed to generate audio")
        else:
            st.error("No text returned from API response")

if __name__ == "__main__":
    main()
