import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_lottie import st_lottie
import requests

# --- COZY PRO STYLING ---
st.markdown("""
<style>
    /* Center the AI Orb */
    .orb-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }
    
    /* Make the mic recorder button invisible but keep it functional */
    div.stButton > button {
        background: rgba(0, 198, 255, 0.05) !important;
        border: 1px solid rgba(0, 198, 255, 0.2) !important;
        color: #00c6ff !important;
        border-radius: 30px !important;
        font-weight: 300 !important;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOADING THE ORB ANIMATION ---
def load_lottie(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# A "Breathing" sphere animation for a professional look
lottie_url = "https://lottie.host/70366657-3069-42b4-84d7-0130985559c5/X6fB1tJk2f.json"
lottie_orb = load_lottie(lottie_url)

with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if lottie_orb:
            st_lottie(lottie_orb, height=200, key="breathing_orb")
        else:
            st.markdown("### 🧠")
        # The trigger remains a subtle, professional text-action
        text = speech_to_text(language='en', start_prompt="🎤 Listening...", stop_prompt="Processing...", just_once=True)

if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="👤"):
        st.write(text)

    if "alexa" in text.lower() or "nexa" in text.lower():
        clean_text = text.lower().replace("alexa", "").replace("nexa", "").strip()
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Refining response..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": clean_text}]
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                speak_web(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})