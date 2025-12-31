import streamlit as st
from streamlit_mic_recorder import speech_to_text
from openai import OpenAI
from gtts import gTTS
import base64
import requests
import uuid
import os

# =========================================================
# CONFIG & AUTH
# =========================================================
st.set_page_config(page_title="NeuralFlex Pro", page_icon="🌙", layout="centered")

MODEL = "openai/gpt-4o-mini"  # High-performance standard model
WAKE_WORDS = ["alexa", "nexa"]

# OpenRouter setup
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# =========================================================
# HELPERS
# =========================================================
def speak(text):
    """Generates and autoplays audio in the browser"""
    try:
        fname = f"speech_{uuid.uuid4().hex}.mp3"
        gTTS(text=text, lang="en").save(fname)
        with open(fname, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"<audio autoplay src='data:audio/mp3;base64,{audio_b64}'></audio>",
            unsafe_allow_html=True
        )
        os.remove(fname)
    except Exception as e:
        st.error(f"Audio Error: {e}")

def extract_command(text):
    """Detects wake words and returns the query"""
    t = text.lower()
    for w in WAKE_WORDS:
        if w in t:
            return t.split(w)[-1].strip()
    return None

# =========================================================
# PREMIUM CHATGPT-STYLE UI
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: radial-gradient(circle at top, #1b1f3b, #05060f);
    color: white;
}

/* ChatGPT Voice Orb Styling */
.orb-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 50px 0;
    position: relative;
}

.voice-orb {
    width: 140px;
    height: 140px;
    background: radial-gradient(circle at 30% 30%, #c4b5fd, #7c3aed);
    border-radius: 50%;
    box-shadow: 0 0 50px rgba(124, 58, 237, 0.5);
    animation: breathe 4s ease-in-out infinite;
    z-index: 1;
}

/* Ripple Animation */
.voice-orb::after {
    content: '';
    position: absolute;
    width: 140px;
    height: 140px;
    border-radius: 50%;
    border: 2px solid #7c3aed;
    animation: ripple 2s linear infinite;
    z-index: 0;
}

@keyframes breathe {
    0%, 100% { transform: scale(1); box-shadow: 0 0 40px rgba(124, 58, 237, 0.5); }
    50% { transform: scale(1.08); box-shadow: 0 0 70px rgba(124, 58, 237, 0.8); }
}

@keyframes ripple {
    0% { transform: scale(1); opacity: 0.8; }
    100% { transform: scale(2); opacity: 0; }
}

/* Hide the actual speech_to_text button and overlay it on the Orb */
div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10;
}

div.stButton > button {
    width: 150px !important;
    height: 150px !important;
    opacity: 0 !important; /* Makes the functional button invisible */
    cursor: pointer;
}

/* Glassmorphism Chat */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px);
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MAIN APP FLOW
# =========================================================
st.title("🌙 NeuralFlex")
st.caption("Next-Gen Voice Intelligence")

# 1. Load Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
        st.markdown(msg["content"])

# 2. Render Orb UI
st.markdown('<div class="orb-container"><div class="voice-orb"></div></div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.6;'>Tap the orb & say \"Alexa\"</p>", unsafe_allow_html=True)

# 3. Hidden Microphone Trigger
# This functional button is perfectly centered over the visual Orb
text = speech_to_text(language="en", just_once=True, key="voice_trigger")

# 4. Processing Logic
if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(text)

    command = extract_command(text)
    
    if not command:
        response_msg = "🌙 I'm listening. Please start your request with **Alexa** or **Nexa**."
        st.session_state.messages.append({"role": "assistant", "content": response_msg})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response_msg)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("⚡ Processing Neural Patterns..."):
                try:
                    chat_completion = client.chat.completions.create(
                        model=MODEL,
                        messages=st.session_state.messages,
                        temperature=0.7
                    )
                    ans = chat_completion.choices[0].message.content
                    st.markdown(ans)
                    speak(ans) # Voice output
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except Exception as e:
                    st.error(f"Neural Link Error: {e}")