# 🎙️ Nexa Web: AI Voice Assistant

<div align="center">

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg.svg)](https://nexa-web.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/Atiqumer/nexa-web?style=social)](https://github.com/Atiqumer/nexa-web)

**A sleek, intelligent, and responsive AI-powered voice assistant built for the web.** *Bridging the gap between human voice and AI intelligence.*

[Explore the App](https://nexa-web.streamlit.app/) • [Report Bug](https://github.com/Atiqumer/nexa-web/issues) • [Request Feature](https://github.com/Atiqumer/nexa-web/issues)

</div>

---

## 📖 Overview

**Nexa Web** is a modern AI-Web Based Voice Assistant designed to provide a hands-free interactive experience. By integrating advanced speech recognition with Python-based backend processing, Nexa allows users to communicate with an AI agent directly through their browser, making information retrieval and task management as simple as speaking.

### 🎥 Visual Preview

| Interface Overview | Live Interaction |
| :---: | :---: |
| <img src="Screenshot%202025-12-31%20224005.png" width="100%" alt="Dashboard Overview"> | <img src="Screenshot%202025-12-31%20224128.png" width="100%" alt="Chat Interaction"> |

---

## ✨ Key Features

- 🎧 **Voice Recognition:** High-fidelity speech-to-text processing for accurate command capture.
- 🧠 **Smart Processing:** Leverages optimized AI logic to understand and fulfill user requests.
- 💻 **Minimalist UI:** A clean, distraction-free dashboard built with Streamlit for maximum usability.
- ⚡ **Lightweight & Fast:** Optimized for low latency, providing near-instantaneous feedback.
- 🌐 **Cloud Native:** Fully compatible with Streamlit Cloud for easy access from any device.

---

## 🛠️ Built With

* **[Python](https://www.python.org/):** The core engine of the application.
* **[Streamlit](https://streamlit.io/):** Used for creating the interactive web interface.
* **SpeechRecognition:** To capture and translate audio into actionable data.
* **Pyttsx3 / Text-to-Speech:** To give the AI its own voice.

---

## 🚀 Getting Started

Follow these steps to set up the project locally on your machine.

### 📋 Prerequisites

* Python 3.10+
* A working microphone
* Internet connection (for API-based speech recognition)

### ⚙️ Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Atiqumer/nexa-web.git](https://github.com/Atiqumer/nexa-web.git)
    cd nexa-web
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Launch the Assistant**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Repository Structure

```text
nexa-web/
├── .devcontainer/      # Development environment configuration
├── app.py              # Main application entry point
├── requirements.txt    # Project dependencies
├── Screenshot...png    # Visual documentation
└── .gitignore          # Files excluded from version control