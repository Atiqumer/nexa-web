import streamlit as st
from streamlit_mic_recorder import speech_to_text
from openai import OpenAI
from gtts import gTTS
import base64
import uuid
import os

# =========================================================
# CONFIG & AUTH
# =========================================================
st.set_page_config(page_title="NeuralFlex Pro", page_icon="🌙", layout="centered")

MODEL = "openai/gpt-4o-mini"
WAKE_WORDS = ["alexa", "nexa"]

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
# PREMIUM UI STYLING
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: radial-gradient(circle at top, #1b1f3b, #05060f);
    color: white;
}

/* ChatGPT Style Voice Orb */
.orb-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 60px 0;
    position: relative;
}

.voice-orb {
    width: 150px;
    height: 150px;
    background: radial-gradient(circle at 30% 30%, #c4b5fd, #7c3aed);
    border-radius: 50%;
    box-shadow: 0 0 60px rgba(124, 58, 237, 0.6);
    animation: breathe 4s ease-in-out infinite;
    z-index: 1;
}

/* Ripple effect */
.voice-orb::after {
    content: '';
    position: absolute;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    border: 3px solid rgba(124, 58, 237, 0.4);
    animation: ripple 2s linear infinite;
    z-index: 0;
}

@keyframes breathe {
    0%, 100% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 80px rgba(124, 58, 237, 0.8); }
}

@keyframes ripple {
    0% { transform: scale(1); opacity: 0.8; }
    100% { transform: scale(2.2); opacity: 0; }
}

/* Hide and Overlay Mic Button */
div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10;
}

div.stButton > button {
    width: 160px !important;
    height: 160px !important;
    opacity: 0 !important;
    cursor: pointer;
    border-radius: 50%;
}

/* Glassmorphism Chat Bubbles */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.04) !important;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MAIN APP FLOW
# =========================================================
st.title("🌙 NeuralFlex Pro")
st.caption("Advanced Voice AI System")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Using Material Symbols for Avatars
for msg in st.session_state.messages:
    avatar = ":material/smart_toy:" if msg["role"] == "assistant" else ":material/person:"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Render Interactive UI
st.markdown('<div class="orb-container"><div class="voice-orb"></div></div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.7;'>Tap the Orb & say <b>\"Alexa\"</b></p>", unsafe_allow_html=True)

# Functional Mic Trigger
text = speech_to_text(language="en", just_once=True, key="voice_trigger")

if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(text)

    command = extract_command(text)
    
    if not command:
        resp = "🌙 I'm listening. Use **Alexa** or **Nexa** to give a command."
        st.session_state.messages.append({"role": "assistant", "content": resp})
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            st.markdown(resp)
    else:
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            with st.spinner("⚡ Connecting to Neural Link..."):
                try:
                    chat_completion = client.chat.completions.create(
                        model=MODEL,
                        messages=st.session_state.messages,
                        temperature=0.7
                    )
                    ans = chat_completion.choices[0].message.content
                    st.markdown(ans)
                    speak(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except Exception as e:
                    st.error(f"Neural Error: {e}")