import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests
import requests
import tempfile
import numpy as np
import wave
import io

from groq import Groq

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
st.title("Voice Recorder XX")
audio_bytes = audio_recorder()

result = ""

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

    client = Groq(
        api_key='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',
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Answer to this query in less thant 20 words as you are a kind voice assistant. The query: "+result['text'],
            }
        ],
        model="llama3-8b-8192",
    )

    st.write("API Response:", chat_completion.choices[0].message.content)

    answer = chat_completion.choices[0].message.content

    # Define the URL and the payload
    url = "https://yh2m49z3xrn07uzh.us-east-1.aws.endpoints.huggingface.cloud"
    payload = {
        "inputs": answer,
        "voice_description": "A male speaker with a low-pitched voice speaks slightly fast."
    }

    # Define the headers, including your Authorization token
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check the response
    if response.status_code == 200:
        print("Success!")
        print("Response JSON:", response.json())
    else:
        print("Failed with status code:", response.status_code)
        print("Response text:", response.text)
        
    # Load audio and save
    json_response = json.dumps(response.json()[0])


    # Parse the JSON response
    data = json.loads(json_response)
    audio_samples = data['generated_audio']

    audio_array = np.array(audio_samples, dtype=np.float32)
    audio_int16 = (audio_array * 32767).astype(np.int16)

    audio_buffer = io.BytesIO()
    with wave.open(audio_buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        wf.writeframes(audio_int16.tobytes())

    audio_buffer.seek(0)

    st.title("Audio Playback in Streamlit")
    st.write("Generated Audio:")

    st.audio(audio_buffer, format='audio/wav')


