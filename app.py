import streamlit as st
from streamlit_mic_recorder import speech_to_text
from openai import OpenAI
from gtts import gTTS
import uuid, base64, os

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(
    page_title="NeuralFlex",
    page_icon="🟣",
    layout="centered"
)

MODEL = "openai/gpt-4o-mini"
WAKE_WORDS = ["alexa", "nexa"]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# ======================================================
# SESSION STATE
# ======================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================================================
# AUDIO OUTPUT
# ======================================================
def speak(text):
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    gTTS(text=text, lang="en").save(filename)
    audio = open(filename, "rb").read()
    b64 = base64.b64encode(audio).decode()
    os.remove(filename)

    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}">
        </audio>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# COMMAND EXTRACTION
# ======================================================
def extract_command(text):
    t = text.lower()
    for w in WAKE_WORDS:
        if w in t:
            return t.replace(w, "").strip()
    return None

# ======================================================
# PREMIUM UI (CSS)
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: radial-gradient(circle at top, #1b1f3b, #070b1f);
    color: white;
}

.card {
    width: 420px;
    margin: 70px auto;
    padding: 45px 30px;
    border-radius: 32px;
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(167,139,250,0.25);
    box-shadow: 0 0 120px rgba(139,92,246,0.4);
    text-align: center;
}

/* ORB */
.orb {
    width: 170px;
    height: 170px;
    margin: 0 auto 25px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #c4b5fd, #7c3aed);
    box-shadow:
        0 0 80px rgba(139,92,246,1),
        inset 0 0 45px rgba(255,255,255,0.4);
    animation: breathe 4s ease-in-out infinite;
    cursor: pointer;
}

@keyframes breathe {
    0%,100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}

/* WAVEFORM */
.waveform {
    display: flex;
    justify-content: center;
    gap: 7px;
    height: 60px;
    margin: 18px 0;
}

.waveform span {
    width: 7px;
    height: 100%;
    background: linear-gradient(#a78bfa, #7c3aed);
    border-radius: 10px;
    animation: wave 1.1s infinite ease-in-out;
}

.waveform span:nth-child(odd) { animation-delay: .2s }
.waveform span:nth-child(even) { animation-delay: .4s }

@keyframes wave {
    0%,100% { height: 25%; opacity: 0.5; }
    50% { height: 100%; opacity: 1; }
}

/* STATUS */
.status {
    font-size: 0.85rem;
    letter-spacing: 0.14em;
    opacity: 0.85;
}

/* HIDE STREAMLIT BUTTONS */
[data-testid="stButton"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# UI MARKUP
# ======================================================
st.markdown("""
<div class="card">
    <div class="orb" onclick="document.getElementById('hidden-btn').click()"></div>

    <div class="waveform">
        <span></span><span></span><span></span>
        <span></span><span></span><span></span><span></span>
    </div>

    <div class="status">
        Click the orb and say “Alexa”
    </div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# HIDDEN MIC BUTTON
# ======================================================
st.button("hidden", key="hidden-btn")

voice = speech_to_text(
    language="en",
    just_once=True,
    key="mic"
)

# ======================================================
# MAIN LOGIC
# ======================================================
if voice:
    st.session_state.messages.append(
        {"role": "user", "content": voice}
    )

    cmd = extract_command(voice)

    if not cmd:
        reply = "Say Alexa or Nexa before your command."
        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
        speak(reply)

    else:
        response = client.chat.completions.create(
            model=MODEL,
            messages=st.session_state.messages,
            temperature=0.6
        )

        answer = response.choices[0].message.content
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        speak(answer)
