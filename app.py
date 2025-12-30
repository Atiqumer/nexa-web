import streamlit as st
from streamlit_mic_recorder import speech_to_text
from openai import OpenAI
from gtts import gTTS
import base64
import os

# --- PAGE UI ---
st.set_page_config(page_title="NeuralFlex AI", page_icon="🧠")
st.title("🧠 NeuralFlex AI Assistant")
st.write("Click the mic and say 'Nexa' followed by your question!")

# --- AUTH SETUP ---
# On the web, we use st.secrets instead of .env for security
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

def speak_web(text):
    """Generates audio and plays it in the user's browser"""
    tts = gTTS(text=text, lang='en')
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        # HTML to make it play automatically
        md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
        st.markdown(md, unsafe_allow_html=True)

# --- THE MICROPHONE ---
# This button works on Mobile (Safari/Chrome) and PC
text = speech_to_text(language='en', start_prompt="🎤 Start Talking", stop_prompt="🛑 Stop")

if text:
    st.write(f"**You:** {text}")
    if "nexa" in text.lower():
        clean_text = text.lower().replace("Nexa", "").strip()
        with st.spinner("Nexa is thinking..."):
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[{"role": "user", "content": clean_text}]
            )
            answer = response.choices[0].message.content
        st.write(f"**Nexa:** {answer}")
        speak_web(answer)