import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie
from openai import OpenAI
from gtts import gTTS
import base64
import requests

# --- 1. PRO PAGE CONFIG ---
st.set_page_config(page_title="NeuralFlex AI", page_icon="🌙", layout="centered")

# --- 2. GLASSMORPHISM CSS ---
st.markdown("""
<style>
    /* Main Background with soft radial gradient */
    .stApp {
        background: radial-gradient(circle at top right, #1b2735 0%, #090a0f 100%);
        color: #e0e0e0;
    }
    
    /* Cozy Glassmorphism Chat Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        padding: 15px !important;
        margin-bottom: 12px;
    }

    /* Minimalist Microphone Button */
    div.stButton > button {
        border-radius: 50px !important;
        border: 1px solid rgba(0, 198, 255, 0.4) !important;
        background: rgba(0, 198, 255, 0.05) !important;
        color: #00c6ff !important;
        height: 3.5rem !important;
        width: 100% !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: rgba(0, 198, 255, 0.15) !important;
        box-shadow: 0 0 20px rgba(0, 198, 255, 0.3);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC ---
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"])

def speak_web(text):
    tts = gTTS(text=text, lang='en')
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. MAIN UI ---
st.title("🌙 NeuralFlex")
st.caption("Intelligent Voice Assistant • v2.0 Pro")

# Display conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# Bottom Interface
st.write("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    text = speech_to_text(language='en', start_prompt="🎤 Tap to Speak", stop_prompt="Listening...", just_once=True)

if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="👤"):
        st.write(text)

    if "alexa" in text.lower() or "nexa" in text.lower():
        clean_text = text.lower().replace("alexa", "").replace("nexa", "").strip()
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Refining response..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b:free",
                    messages=[{"role": "user", "content": clean_text}]
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                speak_web(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})