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
WAKE_WORDS = ["alexa", "nexa"]

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

# =========================================================
# 4. HELPERS
# =========================================================
def extract_command(text):
    text = text.lower()
    for word in WAKE_WORDS:
        if word in text:
            return text.replace(word, "").strip()
    return None


def speak(text):
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
# 5. COZY UI STYLE
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: radial-gradient(circle at top, #1b1f3b, #070b1f);
    color: #eaeaff;
}

.cozy-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(18px);
    border-radius: 28px;
    padding: 35px;
    border: 1px solid rgba(167,139,250,0.25);
    box-shadow: 0 0 45px rgba(139,92,246,0.25);
    max-width: 420px;
    margin: auto;
}

.orb {
    width: 140px;
    height: 140px;
    margin: auto;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #c4b5fd, #7c3aed);
    box-shadow: 0 0 40px #8b5cf6;
    animation: float 4s ease-in-out infinite;
}

@keyframes float {
    0%,100% { transform: translateY(0px); }
    50% { transform: translateY(-14px); }
}

.wave {
    display: flex;
    justify-content: center;
    gap: 6px;
    height: 70px;
    margin: 25px 0;
}

.wave span {
    width: 6px;
    background: linear-gradient(#a78bfa, #7c3aed);
    border-radius: 10px;
    animation: wave 1.2s infinite ease-in-out;
}

.wave span:nth-child(odd) { animation-delay: .2s; }
.wave span:nth-child(even) { animation-delay: .4s; }

@keyframes wave {
    0%,100% { height: 20%; opacity: .5; }
    50% { height: 100%; opacity: 1; }
}

.mic-btn {
    width: 90px;
    height: 90px;
    margin: auto;
    border-radius: 50%;
    background: radial-gradient(circle, #f472b6, #ec4899);
    box-shadow: 0 0 25px #ec4899;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    cursor: pointer;
    transition: transform .2s ease;
}

.mic-btn:hover {
    transform: scale(1.1);
}

.status {
    text-align: center;
    margin-top: 15px;
    letter-spacing: .1em;
    opacity: .85;
}

[data-testid="stButton"] button {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 6. HEADER
# =========================================================
st.markdown("<h1 style='text-align:center'>🌙 NeuralFlex</h1>", unsafe_allow_html=True)
st.caption("Cozy Neural Voice Interface")

# =========================================================
# 7. CHAT HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# =========================================================
# 8. COZY VOICE UI
# =========================================================
st.markdown("""
<div class="cozy-card">
    <div class="orb"></div>

    <div class="wave">
        <span></span><span></span><span></span>
        <span></span><span></span><span></span>
        <span></span>
    </div>

    <div class="mic-btn" onclick="document.getElementById('hidden').click()">
        🎙️
    </div>

    <div class="status" id="statusText">
        Tap to speak (say Alexa or Nexa)
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 9. HIDDEN BUTTON + SPEECH INPUT
# =========================================================
st.button("hidden", key="hidden")

text = speech_to_text(
    language="en",
    just_once=True,
    key="voice"
)

# =========================================================
# 10. MAIN LOGIC
# =========================================================
if text:
    st.session_state.messages.append({"role": "user", "content": text})

    command = extract_command(text)

    if not command:
        reply = "🌙 Please say **Alexa** or **Nexa** before your command."
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
const status = document.getElementById("statusText");
const mic = document.querySelector(".mic-btn");

mic.addEventListener("click", () => {
    status.innerText = "Listening...";
    mic.style.boxShadow = "0 0 40px #ef4444";
});
</script>
""", unsafe_allow_html=True)
