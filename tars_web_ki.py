import streamlit as st
import openai
import requests
import tempfile
import base64

# API-Schlüssel aus Secrets
openai.api_key = st.secrets["openai_key"]
elevenlabs_api_key = st.secrets["eleven_key"]

# Web-Oberfläche
st.set_page_config(page_title="TARS KI", layout="centered")
st.title("TARS - Deine deutschsprachige KI")
st.markdown("**Bereit für den nächsten Befehl, Ramon.**")

# Session-State zum Sperren der Eingabe
if "antwort_laeuft" not in st.session_state:
    st.session_state["antwort_laeuft"] = False

# Steuerregler
humor = st.slider("Humorstufe", 0, 100, 20)
ehrlichkeit = st.slider("Ehrlichkeitsstufe", 0, 100, 100)

# Texteingabe (gesperrt während Antwort)
if st.session_state["antwort_laeuft"]:
    st.text_input("Was möchtest du TARS fragen?", value="Warte auf Antwort...", disabled=True)
    user_input = None
else:
    user_input = st.text_input("Was möchtest du TARS fragen?")

# Prompt erzeugen
def build_prompt(question, humor, ehrlichkeit):
    return f"Du bist TARS, ein KI-Roboter aus dem Film Interstellar. Sprich Deutsch. Deine Antworten sind pragmatisch, manchmal sarkastisch, abhängig von der Humorstufe ({humor}%) und Ehrlichkeitsstufe ({ehrlichkeit}%). Antworte auf: '{question}'"

# ElevenLabs Text-to-Speech mit Autoplay
def speak_with_elevenlabs(text):
    voice_id = "FTNCalFNG5bRnkkaP5Ug"  # Deutsche Stimme
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.7
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        audio_base64 = base64.b64encode(response.content).decode()
        st.markdown(
            f"<audio autoplay controls src='data:audio/mp3;base64,{audio_base64}'></audio>",
            unsafe_allow_html=True
        )
    else:
        st.error(f"Fehler bei der Sprachausgabe von ElevenLabs: {response.status_code} – {response.text}")

# GPT-Antwort erzeugen
if user_input:
    st.session_state["antwort_laeuft"] = True  # Eingabe sperren
    prompt = build_prompt(user_input, humor, ehrlichkeit)
    with st.spinner("TARS denkt nach..."):
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            tars_reply = response.choices[0].message.content.strip()
            st.markdown(f"**TARS sagt:** {tars_reply}")
            speak_with_elevenlabs(tars_reply)
        except Exception as e:
            st.error(f"Fehler bei OpenAI oder ElevenLabs: {e}")
    st.session_state["antwort_laeuft"] = False  # Eingabe wieder freigeben
