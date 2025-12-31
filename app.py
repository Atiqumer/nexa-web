import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie
from openai import OpenAI
from gtts import gTTS
import base64
import requests
import os

# --- 1. PRO PAGE CONFIG ---
st.set_page_config(page_title="NeuralFlex Pro", page_icon="🌙", layout="centered")

# --- 2. MODERN COZY GLASSMORPHISM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: #ffffff;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Enhanced Glassmorphism Chat Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
        padding: 20px !important;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.3);
    }

    /* Mic Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.05)) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        color: #ffffff !important;
        border-radius: 50px !important;
        padding: 16px 32px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1)) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Title Styling */
    h1 {
        text-align: center;
        font-weight: 700;
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0 !important;
        text-shadow: 0 0 40px rgba(255, 255, 255, 0.3);
    }
    
    /* Caption Styling */
    .stCaption {
        text-align: center;
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 1.1rem !important;
        font-weight: 300;
        margin-top: 8px !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(255, 255, 255, 0.3) 50%, 
            transparent 100%);
        margin: 2rem 0;
    }
    
    /* Center Container */
    .center-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 0;
    }
    
    /* Orb Container */
    .orb-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37),
                    inset 0 0 20px rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        background: rgba(76, 175, 80, 0.2);
        border: 1px solid rgba(76, 175, 80, 0.5);
        color: #4caf50;
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        backdrop-filter: blur(10px);
        margin-top: 1rem;
    }
    
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #4caf50;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Spinner Override */
    .stSpinner > div {
        border-top-color: #ffffff !important;
    }
    
    /* Message Content */
    [data-testid="stChatMessage"] p {
        color: #ffffff !important;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. AUTH & HELPERS ---
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"])

def load_lottie(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def speak_web(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Audio error: {e}")

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. MAIN UI ---
lottie_url = "https://lottie.host/70366657-3069-42b4-84d7-0130985559c5/X6fB1tJk2f.json"
lottie_orb = load_lottie(lottie_url)

# Header
st.title("🌙 NeuralFlex")
st.caption("Cozy Edition • Voice-Powered AI Assistant")

# Status Badge
st.markdown("""
    <div style="text-align: center;">
        <span class="status-badge">
            <span class="status-dot"></span>Always Listening
        </span>
    </div>
""", unsafe_allow_html=True)

st.write("")

# Display Chat History
if st.session_state.messages:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
else:
    st.markdown("""
        <div style="text-align: center; padding: 2rem; color: rgba(255, 255, 255, 0.7);">
            <p style="font-size: 1.2rem; margin: 0;">Say "Alexa" or "Nexa" followed by your question</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.8;">Example: "Alexa, what's the weather like?"</p>
        </div>
    """, unsafe_allow_html=True)

# Interaction Area
st.write("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    
    if lottie_orb:
        st.markdown('<div class="orb-container">', unsafe_allow_html=True)
        st_lottie(lottie_orb, height=180, key="orb")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="orb-container" style="font-size: 5rem; text-align: center;">
                🧠
            </div>
        """, unsafe_allow_html=True)
    
    text = speech_to_text(
        language='en', 
        start_prompt="✨ Whisper to NeuralFlex", 
        stop_prompt="🌊 Receiving your voice...", 
        just_once=True,
        key="voice_input"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LOGIC ---
if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="👤"):
        st.write(text)

    if "alexa" in text.lower() or "nexa" in text.lower():
        clean_text = text.lower().replace("alexa", "").replace("nexa", "").strip()
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("✨ NeuralFlex is thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="google/gemini-2.0-flash-exp:free",
                        messages=[{"role": "user", "content": clean_text}]
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    speak_web(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    else:
        with st.chat_message("assistant", avatar="🤖"):
            reminder = "Please start your request with 'Alexa' or 'Nexa' to activate me! 😊"
            st.markdown(reminder)
            st.session_state.messages.append({"role": "assistant", "content": reminder})