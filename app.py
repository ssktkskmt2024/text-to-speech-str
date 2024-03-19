import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64


# OpenAI Whisperを活用し、音声入力から、GPT AIの応答を音声で得るアプリを作成する
# 参考URLをもとに製作
# https://www.youtube.com/watch?v=0-kvvEChjQo
# pip install openai streamlit audio_recorder_streamlitを事前にインストールしておく
# OpenAIのAPIキーを取得しておく このデモでは、StreamlitのサイドバーにAPIキーを入力する形にしている


# initialize openai client
def setup_openai_client(api_key):

    return openai.OpenAI(api_key=api_key)

def transcribe_audio(client, audio_path):

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text
    
# taking response from the Openai
def fetch_ai_response(client, input_text):
    messages = [ {"role": "user", "content": input_text}]
    response = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=messages)
    return response.choices[0].message.content

# convert text to audio
def text_to_audio(client, text, audio_path):
    response = client.audio.speech.create(model="tts-1", voice="echo", input=text)
    response.stream_to_file(audio_path)

# text cards function
def create_text_card(text, title="Response"):
    card_html = f"""
    <style>
        .card {{
            box-shadow: 0 4px 8px 0 rgba(0, 120, 0, 0.2);
            transition: 0.3s;
            border-radius: 5px;
            padding: 15px;
            background-color: #808080;
        }}
        .card:hover {{
            box-shadow: 0 8px 16px 0 rgba(0, 120, 0, 0.2);
        }}
        .container {{
            padding: 2px 16px;
        }}
    </style>
    <div class="card">
        <div class="container">
            <h4>{title}</b></h4>
            <p>{text}</p>
        <div>
    <div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# auto play audio function
def auto_play_audio(audio_file):

    with open(audio_file, "rb") as audio_file:
        audio_bytes = audio_file.read()
        base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        audio_html = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
        st.markdown(audio_html, unsafe_allow_html=True)

def main():
    
    st.sidebar.title("Audio Recorder")
    api_key = st.sidebar.text_input("Enter your Open AI API Key", type="password")

    st.title("Audio to Text")
    st.write("This is a simple web app that converts audio to text using OpenAI's Speech to Text API.")
    

    # chech if api key is there
    if api_key:
        client = setup_openai_client(api_key)
        recorded_audio = audio_recorder()
        # check if audio is done and available
        if recorded_audio:
            audio_file = "audio.mp3"
            with open(audio_file, "wb") as file:
                file.write(recorded_audio)

            transcribed_text = transcribe_audio(client, audio_file)
            create_text_card(transcribed_text, title="Audio Transcription")
            # st.write("Transcribed Text: ", transcribed_text)
            ai_response = fetch_ai_response(client, transcribed_text)
            response_audio_file = "audio_response.mp3"
            text_to_audio(client, ai_response, response_audio_file)
            # st.audio(response_audio_file, format="audio/mp3")
            auto_play_audio(response_audio_file)
            # st.write("AI Response: ", ai_response)
            create_text_card(ai_response, title="AI Response")

if __name__ == "__main__":
    main()