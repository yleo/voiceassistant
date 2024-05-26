import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests
import tempfile
import base64

# Hugging Face API endpoint and headers
endpoint_url = "https://v2owhjkjdnkfhp30.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "audio/wav"
}

# Function to send audio file to Hugging Face API
def send_to_api(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        response = requests.post(endpoint_url, headers=headers, data=data)
    
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return {"error": f"Failed to get a valid response: {response.status_code}, {response.text}"}

# Record audio
st.title("Voice Recorder P")
audio_bytes = audio_recorder()

if audio_bytes:
    # Save the recorded audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name
    
    # Play the recorded audio
    st.audio(audio_bytes, format="audio/wav")
    
    # Send the audio file to the API and display the result
    with st.spinner("Sending audio to API..."):
        result = send_to_api(temp_file_path)
    
    st.write("API Response:", result)

from groq import Groq

client = Groq(
    api_key='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',
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Answer to this query in less thant 20 words as you are a kind voice assistant. The query: "+result,
        }
    ],
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)
