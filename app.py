import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie
from openai import OpenAI
from gtts import gTTS
import base64
import requests
import os

# --- 1. PRO PAGE CONFIG & THEME ---
st.set_page_config(page_title="NeuralFlex Pro", page_icon="🧠", layout="centered")

# Professional CSS Injection
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stChatFloatingInputContainer { background-color: #161B22; border-top: 1px solid #30363D; }
    [data-testid="stChatMessage"] { background-color: #1F2937; border-radius: 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & ASSETS ---
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"])

def load_lottie(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def speak_web(text):
    tts = gTTS(text=text, lang='en')
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)

# --- 3. SIDEBAR & STATE ---
with st.sidebar:
    st.title("⚙️ NeuralFlex Settings")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
    st.info("Version: Pro 1.0")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I assist you today?"}]

# --- 4. MAIN UI ---
lottie_ai = load_lottie("https://assets5.lottiefiles.com/packages/lf20_q8ND1A8ibK.json") # Replace with your URL
if lottie_ai:
    st_lottie(lottie_ai, height=200, key="ai_icon")

st.title("NeuralFlex Voice Assistant")

# Display conversation using professional chat elements
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Microphone Interface
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    text = speech_to_text(language='en', start_prompt="🎤 Pulse to Talk", stop_prompt="🛑 Processing...", just_once=True)

if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.write(text)

    # Wake word detection
    if "alexa" in text.lower() or "nexa" in text.lower():
        clean_text = text.lower().replace("alexa", "").replace("nexa", "").strip()
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = client.chat.completions.create(
                    model="openai/gpt-3.5-turbo",
                    messages=[{"role": "user", "content": clean_text}]
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                speak_web(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})