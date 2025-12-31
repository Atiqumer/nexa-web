import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie
from openai import OpenAI
from gtts import gTTS
import base64
import requests
import os

# --- 1. PRO PAGE CONFIG ---
st.set_page_config(page_title="NeuralFlex Pro", page_icon="🌙", layout="centered")

# --- 2. COZY GLASSMORPHISM CSS ---
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top right, #1b2735 0%, #090a0f 100%);
        color: #e0e0e0;
    }
    
    /* Cozy Glassmorphism Chat Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        padding: 15px !important;
        margin-bottom: 12px;
    }

    /* Invisible but functional Mic Button */
    div.stButton > button {
        background: rgba(0, 198, 255, 0.05) !important;
        border: 1px solid rgba(0, 198, 255, 0.2) !important;
        color: #00c6ff !important;
        border-radius: 30px !important;
        width: 100% !important;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. AUTH & HELPERS ---
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"])

def load_lottie(url):
    return requests.get(url).json()

# A "Breathing" sphere animation for a professional look
lottie_orb = load_lottie("https://lottie.host/df32c1c6-3023-455a-9f5b-513697e87600/1X6M6s9S7V.json")

with st.container():
    st.write("") # Spacer
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st_lottie(lottie_orb, height=200, key="breathing_orb")
        # The trigger remains a subtle, professional text-action
        text = speech_to_text(language='en', start_prompt="🎤 Listening...", stop_prompt="Processing...", just_once=True)

# --- 6. LOGIC ---
if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="👤"):
        st.write(text)

    if "alexa" in text.lower() or "nexa" in text.lower():
        clean_text = text.lower().replace("alexa", "").replace("nexa", "").strip()
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("NeuralFlex is thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="google/gemini-2.0-flash-exp:free", # Using a reliable free model
                        messages=[{"role": "user", "content": clean_text}]
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    speak_web(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {e}")