import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie
from openai import OpenAI
from gtts import gTTS
import base64
import requests
import uuid
import os

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="NeuralFlex",
    page_icon="🌙",
    layout="centered"
)

MODEL = "openai/gpt-4o-mini"
WAKE_WORDS = ["alexa", "nexa"]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# =========================================================
# HELPERS
# =========================================================
def load_lottie(url):
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def speak(text):
    try:
        fname = f"speech_{uuid.uuid4().hex}.mp3"
        gTTS(text=text, lang="en").save(fname)
        with open(fname, "rb") as f:
            audio = base64.b64encode(f.read()).decode()
        st.markdown(
            f"<audio autoplay src='data:audio/mp3;base64,{audio}'></audio>",
            unsafe_allow_html=True
        )
        os.remove(fname)
    except Exception as e:
        st.error(e)


def extract_command(text):
    t = text.lower()
    for w in WAKE_WORDS:
        if w in t:
            return t.replace(w, "").strip()
    return None


# =========================================================
# STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================================================
# STYLES — PREMIUM UI
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: radial-gradient(circle at top, #1b1f3b, #05060f);
    color: white;
}

/* Hide Streamlit button */
div.stButton > button {
    opacity: 0;
    height: 0;
    width: 0;
}

/* Orb */
.orb {
    width: 140px;
    height: 140px;
    margin: auto;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #c4b5fd, #7c3aed);
    box-shadow:
        0 0 40px rgba(124,58,237,.8),
        inset 0 0 30px rgba(255,255,255,.2);
    animation: float 4s ease-in-out infinite;
    cursor: pointer;
}

@keyframes float {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-14px); }
}

/* Waveform */
.wave {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin-top: 25px;
}

.wave span {
    width: 6px;
    height: 20px;
    background: linear-gradient(#a78bfa, #7c3aed);
    border-radius: 6px;
    animation: wave 1.2s infinite ease-in-out;
}

.wave span:nth-child(odd) { animation-delay: .2s }
.wave span:nth-child(even) { animation-delay: .4s }

@keyframes wave {
    0% { height: 18px; opacity: .6; }
    50% { height: 48px; opacity: 1; }
    100% { height: 18px; opacity: .6; }
}

/* Status */
.status {
    text-align: center;
    margin-top: 16px;
    letter-spacing: .1em;
    opacity: .8;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,.05);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 18px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.title("🌙 NeuralFlex")
st.caption("Neural Voice Interface")

# =========================================================
# CHAT
# =========================================================
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
        st.markdown(m["content"])

# =========================================================
# ORB UI
# =========================================================
st.markdown("""
<div class="orb" onclick="document.getElementById('mic-btn').click()"></div>

<div class="wave">
  <span></span><span></span><span></span><span></span>
  <span></span><span></span><span></span><span></span>
</div>

<div class="status">Tap the orb & say “Alexa”</div>
""", unsafe_allow_html=True)

# =========================================================
# HIDDEN MIC TRIGGER
# =========================================================
st.button("hidden", key="mic-btn")

text = speech_to_text(
    language="en",
    just_once=True,
    key="voice"
)

# =========================================================
# LOGIC
# =========================================================
if text:
    st.session_state.messages.append({"role": "user", "content": text})

    command = extract_command(text)

    if not command:
        msg = "🌙 Say **Alexa** or **Nexa** followed by your request."
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.chat_message("assistant"):
            st.markdown(msg)
    else:
        with st.chat_message("assistant"):
            with st.spinner("⚡ Neural processing..."):
                r = client.chat.completions.create(
                    model=MODEL,
                    messages=st.session_state.messages,
                    temperature=0.6
                )
                ans = r.choices[0].message.content
                st.markdown(ans)
                speak(ans)
                st.session_state.messages.append(
                    {"role": "assistant", "content": ans}
                )
