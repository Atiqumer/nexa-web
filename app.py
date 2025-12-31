import streamlit as st
from streamlit_mic_recorder import speech_to_text
from openai import OpenAI
from gtts import gTTS
import base64
import uuid
import os

# =========================================================
# 1. APP CONFIG
# =========================================================
st.set_page_config(
    page_title="NeuralFlex",
    page_icon="🌙",
    layout="centered"
)

MODEL_NAME = "openai/gpt-4o-mini"
WAKE_WORDS = ["alexa"]

# =========================================================
# 2. OPENROUTER CLIENT
# =========================================================
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# =========================================================
# 3. SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "listening" not in st.session_state:
    st.session_state.listening = False

# =========================================================
# 4. HELPERS
# =========================================================
def extract_command(text: str):
    text = text.lower()
    for w in WAKE_WORDS:
        if w in text:
            return text.replace(w, "").strip()
    return None


def speak(text: str):
    filename = f"speech_{uuid.uuid4().hex}.mp3"
    gTTS(text=text, lang="en").save(filename)

    with open(filename, "rb") as f:
        audio = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )

    os.remove(filename)

# =========================================================
# 5. PREMIUM COZY UI (NO BUTTON)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: radial-gradient(circle at top, #1b1f3b, #070b1f);
    color: #eaeaff;
}

/* Card */
.neural-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(22px);
    border-radius: 32px;
    padding: 45px 30px;
    max-width: 420px;
    margin: 40px auto;
    box-shadow: 0 0 90px rgba(139,92,246,0.35);
    border: 1px solid rgba(167,139,250,0.25);
}

/* Orb */
.neural-orb {
    width: 170px;
    height: 170px;
    margin: auto;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #c4b5fd, #7c3aed);
    box-shadow:
        0 0 60px rgba(139,92,246,0.9),
        inset 0 0 40px rgba(255,255,255,0.35);
    animation: breathe 4s ease-in-out infinite;
    cursor: pointer;
}

@keyframes breathe {
    0%,100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}

.neural-orb.listening {
    animation: pulse 1s infinite;
    box-shadow: 0 0 70px rgba(239,68,68,1);
}

@keyframes pulse {
    0%,100% { transform: scale(1); }
    50% { transform: scale(1.15); }
}

/* Waveform */
.waveform {
    display: flex;
    justify-content: center;
    gap: 7px;
    height: 70px;
    margin: 35px 0 10px;
}

.waveform span {
    width: 7px;
    background: linear-gradient(#a78bfa, #7c3aed);
    border-radius: 10px;
    animation: wave 1.4s infinite ease-in-out;
    opacity: 0.75;
}

.waveform span:nth-child(odd) { animation-delay: .2s; }
.waveform span:nth-child(even) { animation-delay: .5s; }

@keyframes wave {
    0%,100% { height: 25%; }
    50% { height: 100%; }
}

/* Status */
.status {
    text-align: center;
    font-size: 0.85rem;
    letter-spacing: .14em;
    opacity: .8;
}

/* Hide Streamlit button */
[data-testid="stButton"] button {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 6. HEADER
# =========================================================
st.markdown("<h1 style='text-align:center'>🌙 NeuralFlex</h1>", unsafe_allow_html=True)
st.caption("A cozy neural voice companion")

# =========================================================
# 7. CHAT HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# =========================================================
# 8. ORB INTERFACE (NO BUTTON)
# =========================================================
st.markdown("""
<div class="neural-card">
    <div class="neural-orb" id="orb"></div>

    <div class="waveform">
        <span></span><span></span><span></span>
        <span></span><span></span><span></span>
        <span></span>
    </div>

    <div class="status" id="statusText">
        Click the orb and say “Alexa” ”
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 9. HIDDEN RECORDER
# =========================================================
st.button("hidden_recorder", key="hidden_recorder")

text = speech_to_text(
    language="en",
    just_once=True,
    key="voice"
)

if text:
    st.session_state.messages.append({"role": "user", "content": text})

    command = extract_command(text)

    if not command:
        reply = "🌙 Please wake me by saying **Alexa** ."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reply)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("⚡ Thinking..."):
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    temperature=0.6,
                    messages=st.session_state.messages
                )

                answer = response.choices[0].message.content
                st.markdown(answer)
                speak(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

st.markdown("""
<script>
const orb = document.getElementById("orb");
const status = document.getElementById("statusText");

orb.addEventListener("click", () => {
    status.innerText = "Listening...";
    orb.classList.add("listening");
    document.getElementById("hidden_recorder").click();

    setTimeout(() => {
        orb.classList.remove("listening");
        status.innerText = "Processing...";
    }, 3500);
});
</script>
""", unsafe_allow_html=True)
