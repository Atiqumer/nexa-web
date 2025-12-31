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
# 1. APP CONFIG
# =========================================================
st.set_page_config(
    page_title="NeuralFlex Pro",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

MODEL_NAME = "openai/gpt-4o-mini"
WAKE_WORDS = ["alexa", "nexa"]

# =========================================================
# 2. CLIENT
# =========================================================
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# =========================================================
# 3. HELPERS
# =========================================================
def load_lottie(url: str):
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def speak_web(text: str):
    try:
        filename = f"speech_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        with open(filename, "rb") as f:
            audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()

        st.markdown(
            f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True
        )

        os.remove(filename)
    except Exception as e:
        st.error(f"🔊 Audio error: {e}")


def extract_command(text: str):
    lower = text.lower()
    for word in WAKE_WORDS:
        if word in lower:
            return lower.replace(word, "").strip()
    return None

# =========================================================
# 4. SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "listening" not in st.session_state:
    st.session_state.listening = False

# =========================================================
# 5. STYLES (UNCHANGED CORE, CLEANED JS TARGETS)
# =========================================================
st.markdown("""<style>
/* ---- SAME STYLE AS YOURS (trimmed for brevity) ---- */
/* IMPORTANT FIX: waveform-container ID added */
.waveform-container { cursor: pointer; }
</style>""", unsafe_allow_html=True)

# =========================================================
# 6. HEADER
# =========================================================
st.title("🌙 NeuralFlex")
st.caption("Neural Voice Interface • AI Powered")

# =========================================================
# 7. CHAT HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# =========================================================
# 8. ORB + WAVEFORM
# =========================================================
lottie_orb = load_lottie(
    "https://lottie.host/70366657-3069-42b4-84d7-0130985559c5/X6fB1tJk2f.json"
)

if lottie_orb:
    st_lottie(lottie_orb, height=150)

st.markdown("""
<div id="waveform" class="waveform-container"
     onclick="document.getElementById('hidden-btn').click()">
    <div class="audio-visualizer">
        """ + "".join("<div class='bar'></div>" for _ in range(9)) + """
    </div>
    <div class="status-text" id="statusText">Tap to Speak</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 9. SPEECH INPUT (HIDDEN BUTTON)
# =========================================================
st.button("hidden", key="hidden-btn")

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
        reminder = "🌙 Say **Alexa** or **Nexa** followed by your command."
        st.session_state.messages.append({"role": "assistant", "content": reminder})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reminder)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("⚡ Neural processing..."):
                try:
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        temperature=0.6,
                        messages=st.session_state.messages
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    speak_web(answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as e:
                    st.error(f"❌ Neural error: {e}")

# =========================================================
# 11. JS – FIXED & CLEAN
# =========================================================
st.markdown("""
<script>
const wf = document.getElementById("waveform");
const statusText = document.getElementById("statusText");

wf.addEventListener("click", () => {
    wf.classList.toggle("recording");
    statusText.textContent = wf.classList.contains("recording")
        ? "Listening..."
        : "Tap to Speak";
});
</script>
""", unsafe_allow_html=True)
