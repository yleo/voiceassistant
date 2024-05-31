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

def get_conference_data(info_type='information_confs'):
    """btenir une brève description de la conférence ou des informations sur le déroulement, les intervenants des différentes conférences en fonction de l'argument info_type.

    Args:
        info_type (str): Type d'information à récupérer ('description' ou 'information_confs').

    Returns:
        str: Chaîne JSON de l'information demandée sur la conférence.
    """
    # Load JSON data
    with open('conference_data.json', encoding='utf-8') as f:
        conference_data = json.load(f)

    if info_type == 'description':
        return json.dumps(conference_data['description'], ensure_ascii=False)
    else:
        return json.dumps(conference_data['timeline'], ensure_ascii=False)

def get_llm_response(user_prompt):
    system_prompt = '''
    Tu es un modèle de langage d'appel de fonction, et tu es chargé de répondre à des questions concernant la conférence EMERTON : Le vrai enjeu de l'IA générative lors du DATA & AI for Business Forum and Meetings.
    Ces informations sont stockées dans un fichier JSON avec une description de la conférence et un planning des différentes sessions.
    Les deux sections sont accessibles via les clés 'description' et 'timeline' respectivement.
    Étant donné une question d'un utilisateur sur la conférence, détermine le type d'information à récupérer.
    Si la question porte sur une présentation de la conférence, appelle get_conference_data avec l'argument 'description'.
    Pour toutes les autres questions pouvant notamment porter sur les intervenants, les horaires, les titres des conférences, appelle get_conference_data avec l'argument 'information_confs'.
    Si tu n'es pas en mesure de répondre à la question de l'utilisateur, appelle get_conference_data avec l'argument 'information_confs' pour obtenir des informations générales sur la conférence.

    TA REPONSE FINALE DOIT ETRE COURTE, CONCISE ET EN FRANCAIS.
    '''

    client = Groq(api_key=LLM_API_KEY)
    MODEL = 'llama3-70b-8192'

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_conference_data",
                "description": "Obtenir une brève description de la conférence ou des informations sur le déroulement, les intervenants des différentes conférences en fonction de l'argument info_type.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    print(f"Tool calls: {tool_calls}")
    if tool_calls:
        available_functions = {
            "get_conference_data": get_conference_data,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            try:
                function_response = function_to_call(**function_args)
            except Exception :
                function_args = {'info_type': 'information_confs'}
                function_response = function_to_call(**function_args)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=4096
        )
    return second_response.choices[0].message.content

# Function to generate audio response
def generate_audio_response(answer):

    # Define the local paths for the model and configuration files
    model_path = "fr_FR-upmc-medium.onnx"
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
