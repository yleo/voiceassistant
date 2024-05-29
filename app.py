import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests
import tempfile
import json
import numpy as np
import wave
import io
from groq import Groq

# Global Variables for API Endpoints and Tokens
HUGGING_FACE_API_ENDPOINT = "https://v2owhjkjdnkfhp30.us-east-1.aws.endpoints.huggingface.cloud"
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
                "content": f"Answer to this query in less than 20 words as you are a kind voice assistant. The query: {query_text}",
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Function to generate audio response
def generate_audio_response(answer):
    payload = {
        "inputs": answer,
        "voice_description": "A male speaker with a low-pitched voice speaks slightly fast."
    }
    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(HUGGING_FACE_AUDIO_ENDPOINT, headers=headers, data=json.dumps(payload))
    return response

# Main function
def main():
    st.title("Voice Recorder X")
    audio_bytes = audio_recorder()
    result = ""

    if audio_bytes:
        result = process_audio(audio_bytes)
        st.write("API Response:", result)
        
        if 'text' in result:
            answer = get_llm_response(result['text'])
            st.write("Groq Response:", answer)
            
            response = generate_audio_response(answer)
            
            if response.status_code == 200:
                data = response.json()
                audio_samples = data[0]['generated_audio']
                
                audio_array = np.array(audio_samples, dtype=np.float32)
                audio_int16 = (audio_array * 32767).astype(np.int16)
                
                audio_buffer = io.BytesIO()
                with wave.open(audio_buffer, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(44100)
                    wf.writeframes(audio_int16.tobytes())
                
                audio_buffer.seek(0)
                
                st.title("Audio Playback in Streamlit")
                st.write("Generated Audio:")
                st.audio(audio_buffer, format='audio/wav')
            else:
                st.error(f"Failed with status code: {response.status_code}, {response.text}")
        else:
            st.error("No text returned from API response")

if __name__ == "__main__":
    main()
