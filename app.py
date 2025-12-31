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
st.set_page_config(page_title="Nexa Voice", page_icon="✨", layout="centered")

MODEL = "openai/gpt-4o-mini"
WAKE_WORDS = ["nexa", "alexa"]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# =========================================================
# HELPERS
# =========================================================
def speak(text):
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
    t = text.lower()
    for w in WAKE_WORDS:
        if w in t:
            return t.split(w)[-1].strip()
    return None

# =========================================================
# CLEAN PROFESSIONAL STYLING (Fixed Layout)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: radial-gradient(circle at top, #1b1f3b, #05060f);
    color: white;
}

/* Glassmorphism Chat Bubbles */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px !important;
    margin-bottom: 10px;
}

/* Centered Interaction Area */
.orb-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 20px 0;
}

.voice-orb {
    width: 150px;
    height: 150px;
    background: radial-gradient(circle at 30% 30%, #c4b5fd, #7c3aed);
    border-radius: 50%;
    box-shadow: 0 0 50px rgba(124, 58, 237, 0.5);
    animation: breathe 4s ease-in-out infinite;
    margin-bottom: 20px;
}

@keyframes breathe {
    0%, 100% { transform: scale(1); box-shadow: 0 0 40px rgba(124, 58, 237, 0.4); }
    50% { transform: scale(1.05); box-shadow: 0 0 70px rgba(124, 58, 237, 0.7); }
}

/* Standardized Mic Button Styling */
div.stButton > button {
    background-color: rgba(124, 58, 237, 0.2) !important;
    color: white !important;
    border: 1px solid #7c3aed !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MAIN APP FLOW
# =========================================================
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>〰️ NEXA Voice</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.7; font-weight: 400;'>Neural Voice Assistant</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.7; font-weight: 200;'>A professional neural voice interface for hands-free AI interaction</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for msg in st.session_state.messages:
    avatar = ":material/smart_toy:" if msg["role"] == "assistant" else ":material/person:"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- CENTERED INTERACTION SECTION ---
st.markdown('<div class="orb-section"><div class="voice-orb"></div></div>', unsafe_allow_html=True)

# Microphone Button (Clean and centered naturally)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    text = speech_to_text(language="en", start_prompt="🎤 Tap to Speak", just_once=True, key="voice_trigger")

st.markdown("<p style='text-align: center; opacity: 0.5; font-size: 0.8rem; margin-top: 10px;'>SAY \"ALEXA\" TO ACTIVATE</p>", unsafe_allow_html=True)

# =========================================================
# LOGIC
# =========================================================
if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(text)

    command = extract_command(text)
    
    if not command:
        resp = "💡 Please include the wake word **Alexa** to activate the link."
        st.session_state.messages.append({"role": "assistant", "content": resp})
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            st.markdown(resp)
    else:
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            with st.spinner("⚡ Processing..."):
                try:
                    chat_completion = client.chat.completions.create(
                        model=MODEL,
                        messages=st.session_state.messages
                    )
                    ans = chat_completion.choices[0].message.content
                    st.markdown(ans)
                    speak(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except Exception as e:
                    st.error(f"Error: {e}")