import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie
from openai import OpenAI
from gtts import gTTS
import base64
import requests
import os

# --- 1. PAGE CONFIG & UI THEME ---
st.set_page_config(page_title="NeuralFlex AI", page_icon="🧠", layout="centered")

# Custom CSS for a sleek, modern look
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .stButton > button {
        border-radius: 20px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
        transition: 0.3s;
        border: none;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #00c6ff;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTH & ASSETS ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def load_lottie(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

# --- 3. HELPER FUNCTIONS ---
def speak_web(text):
    tts = gTTS(text=text, lang='en')
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
        st.markdown(md, unsafe_allow_html=True)

# --- 4. SESSION STATE (Chat History) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. MAIN UI ---
lottie_url = "https://lottie.host/7900b462-811c-4b53-9118-2e0084f6797b/2E351s7VpY.json"# Replace with real URL
lottie_ai = load_lottieurl(lottie_url)

st.title("NeuralFlex Voice Assistant")

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. VOICE INPUT ---
# Center the microphone button using columns
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    text = speech_to_text(language='en', start_prompt="🎤 Speak to Alexa", stop_prompt="🛑 Stop")

if text:
    # Add User message to chat
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.write(text)

    # Process if wake word 'Alexa' is found
    if "Alexa" in text.lower():
        clean_text = text.lower().replace("alexa", "").strip()
        
        with st.chat_message("assistant"):
            with st.spinner("Alexa is thinking..."):
                response = client.chat.completions.create(
                    model="openai/gpt-3.5-turbo",
                    messages=[{"role": "user", "content": clean_text}]
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                speak_web(answer)
                
        # Save Assistant message
        st.session_state.messages.append({"role": "assistant", "content": answer})