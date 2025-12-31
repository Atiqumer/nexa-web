import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie
from openai import OpenAI
from gtts import gTTS
import base64
import requests
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="NeuralFlex AI", page_icon="🧠", layout="centered")

# --- 2. AUTH & ASSETS ---
# Ensure your OPENROUTER_API_KEY is in Streamlit Secrets!
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["OPENROUTER_API_KEY"]
    )
except Exception as e:
    st.error("API Key not found in Streamlit Secrets.")

def speak_web(text):
    tts = gTTS(text=text, lang='en')
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
        st.markdown(md, unsafe_allow_html=True)

# --- 3. UI ---
st.title("NeuralFlex Voice Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. VOICE INPUT ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Added just_once=True to prevent double-triggering
    text = speech_to_text(language='en', start_prompt="🎤 Speak to Alexa", stop_prompt="🛑 Stop", just_once=True)

if text:
    # DEBUG: Show what was heard
    # st.write(f"DEBUG Heard: {text}") 

    if "alexa" in text.lower(): # Changed "Alexa" to lowercase "alexa"
        st.session_state.messages.append({"role": "user", "content": text})
        with st.chat_message("user"):
            st.write(text)

        clean_text = text.lower().replace("alexa", "").strip()
        
        with st.chat_message("assistant"):
            with st.spinner("Alexa is thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="openai/gpt-3.5-turbo", # Double-check model availability
                        messages=[{"role": "user", "content": clean_text}]
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    speak_web(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"AI Error: {e}") # Show API errors directly