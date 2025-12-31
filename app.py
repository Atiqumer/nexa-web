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

# --- 2. FUTURISTIC UI WITH LIVE WAVEFORM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .stApp {
        background: #0a0e27;
        background-image: 
            radial-gradient(at 20% 80%, rgba(120, 119, 198, 0.3) 0px, transparent 50%),
            radial-gradient(at 80% 20%, rgba(99, 102, 241, 0.3) 0px, transparent 50%),
            radial-gradient(at 40% 40%, rgba(139, 92, 246, 0.2) 0px, transparent 50%);
        color: #ffffff;
        overflow-x: hidden;
    }
    
    /* Enhanced Glassmorphism Chat Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(139, 92, 246, 0.2),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
        padding: 20px !important;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateX(4px);
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 12px 40px 0 rgba(139, 92, 246, 0.3),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
    }

    /* Hide default button */
    div.stButton > button {
        display: none !important;
    }
    
    /* Title Styling */
    h1 {
        text-align: center;
        font-weight: 700;
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0 !important;
        letter-spacing: -0.02em;
    }
    
    /* Caption Styling */
    .stCaption {
        text-align: center;
        color: rgba(167, 139, 250, 0.8) !important;
        font-size: 1rem !important;
        font-weight: 300;
        margin-top: 8px !important;
        letter-spacing: 0.05em;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(139, 92, 246, 0.5) 50%, 
            transparent 100%);
        margin: 2rem 0;
    }
    
    /* Waveform Container */
    .waveform-container {
        position: relative;
        width: 100%;
        max-width: 400px;
        margin: 2rem auto;
        padding: 40px;
        background: rgba(139, 92, 246, 0.05);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(139, 92, 246, 0.3);
        border-radius: 30px;
        box-shadow: 0 20px 60px rgba(139, 92, 246, 0.2),
                    inset 0 0 40px rgba(139, 92, 246, 0.1);
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .waveform-container:hover {
        transform: translateY(-5px);
        border-color: rgba(139, 92, 246, 0.6);
        box-shadow: 0 25px 70px rgba(139, 92, 246, 0.4),
                    inset 0 0 50px rgba(139, 92, 246, 0.15);
    }
    
    .waveform-container:active {
        transform: scale(0.98);
    }
    
    /* Audio Waveform Bars */
    .audio-visualizer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        height: 100px;
        margin-bottom: 20px;
    }
    
    .bar {
        width: 6px;
        background: linear-gradient(180deg, #a78bfa 0%, #7c3aed 100%);
        border-radius: 10px;
        animation: wave 1.2s ease-in-out infinite;
        box-shadow: 0 0 10px rgba(167, 139, 250, 0.5);
    }
    
    .bar:nth-child(1) { height: 30%; animation-delay: 0s; }
    .bar:nth-child(2) { height: 50%; animation-delay: 0.1s; }
    .bar:nth-child(3) { height: 70%; animation-delay: 0.2s; }
    .bar:nth-child(4) { height: 90%; animation-delay: 0.3s; }
    .bar:nth-child(5) { height: 100%; animation-delay: 0.4s; }
    .bar:nth-child(6) { height: 90%; animation-delay: 0.5s; }
    .bar:nth-child(7) { height: 70%; animation-delay: 0.6s; }
    .bar:nth-child(8) { height: 50%; animation-delay: 0.7s; }
    .bar:nth-child(9) { height: 30%; animation-delay: 0.8s; }
    
    @keyframes wave {
        0%, 100% { transform: scaleY(1); opacity: 0.7; }
        50% { transform: scaleY(1.5); opacity: 1; }
    }
    
    /* Recording State Animation */
    .recording .bar {
        animation: recording 0.6s ease-in-out infinite;
        background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.8);
    }
    
    @keyframes recording {
        0%, 100% { transform: scaleY(0.5); }
        50% { transform: scaleY(1.8); }
    }
    
    /* Pulse Ring Effect */
    .pulse-ring {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 120%;
        height: 120%;
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 30px;
        animation: pulse-ring 2s ease-out infinite;
    }
    
    @keyframes pulse-ring {
        0% {
            transform: translate(-50%, -50%) scale(0.8);
            opacity: 1;
        }
        100% {
            transform: translate(-50%, -50%) scale(1.2);
            opacity: 0;
        }
    }
    
    /* Status Text */
    .status-text {
        text-align: center;
        color: rgba(167, 139, 250, 0.9);
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .recording-text {
        color: #ef4444;
        animation: blink 1s ease-in-out infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Neural Network Background Effect */
    .neural-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        opacity: 0.1;
        z-index: 0;
    }
    
    /* Orb Container */
    .orb-container {
        background: rgba(139, 92, 246, 0.1);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(139, 92, 246, 0.3);
        border-radius: 50%;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(139, 92, 246, 0.3),
                    inset 0 0 30px rgba(167, 139, 250, 0.2);
        margin-bottom: 2rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(5deg); }
    }
    
    /* Message Content */
    [data-testid="stChatMessage"] p {
        color: #e0e0e0 !important;
        line-height: 1.7;
        font-size: 1rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(139, 92, 246, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.3);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.5);
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
if "is_listening" not in st.session_state:
    st.session_state.is_listening = False

# --- 5. MAIN UI ---
lottie_url = "https://lottie.host/70366657-3069-42b4-84d7-0130985559c5/X6fB1tJk2f.json"
lottie_orb = load_lottie(lottie_url)

# Header
st.title("🌙 NeuralFlex")
st.caption("Neural Voice Interface • Powered by AI")

st.write("")

# Display Chat History
if st.session_state.messages:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
else:
    st.markdown("""
        <div style="text-align: center; padding: 2rem; color: rgba(167, 139, 250, 0.7);">
            <p style="font-size: 1.2rem; margin: 0;">Activate with "Alexa" or "Nexa"</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.8;">Click the waveform to begin transmission</p>
        </div>
    """, unsafe_allow_html=True)

# Interaction Area
st.write("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Orb with Lottie
    if lottie_orb:
        st.markdown('<div class="orb-container">', unsafe_allow_html=True)
        st_lottie(lottie_orb, height=150, key="orb")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Live Audio Waveform Visualizer
    st.markdown("""
        <div class="waveform-container" id="waveform">
            <div class="pulse-ring"></div>
            <div class="audio-visualizer">
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
            </div>
            <div class="status-text">Ready to Listen</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Hidden speech input component
    text = speech_to_text(
        language='en',
        start_prompt="",
        stop_prompt="",
        just_once=True,
        key="voice_input"
    )

# --- 6. LOGIC ---
if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="👤"):
        st.write(text)

    if "alexa" in text.lower() or "nexa" in text.lower():
        clean_text = text.lower().replace("alexa", "").replace("nexa", "").strip()
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("⚡ Processing neural signals..."):
                try:
                    response = client.chat.completions.create(
                        model="google/gemini-2.0-flash-exp",
                        messages=[{"role": "user", "content": clean_text}]
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    speak_web(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"❌ Neural Link Error: {e}")
    else:
        with st.chat_message("assistant", avatar="🤖"):
            reminder = "🌙 Neural link inactive. Please say 'Alexa' or 'Nexa' to establish connection."
            st.markdown(reminder)
            st.session_state.messages.append({"role": "assistant", "content": reminder})

# Add JavaScript for dynamic waveform animation on click
st.markdown("""
<script>
    const waveform = document.getElementById('waveform');
    if (waveform) {
        waveform.addEventListener('click', function() {
            const visualizer = this.querySelector('.audio-visualizer');
            const statusText = this.querySelector('.status-text');
            
            if (!visualizer.classList.contains('recording')) {
                visualizer.classList.add('recording');
                statusText.textContent = 'Recording...';
                statusText.classList.add('recording-text');
            } else {
                visualizer.classList.remove('recording');
                statusText.textContent = 'Ready to Listen';
                statusText.classList.remove('recording-text');
            }
        });
    }
</script>
""", unsafe_allow_html=True)