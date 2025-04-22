import streamlit as st
import openai
from gtts import gTTS
import tempfile
import os

# OpenAI-API-Key (ersetzt diesen String durch deinen echten Key)
openai.api_key = st.secrets["openai_key"]

st.set_page_config(page_title="TARS KI", layout="centered")
st.title("TARS - Deine deutschsprachige KI")

st.markdown("**Bereit für den nächsten Befehl, Ramon.**")

humor = st.slider("Humorstufe", 0, 100, 20)
ehrlichkeit = st.slider("Ehrlichkeitsstufe", 0, 100, 100)

user_input = st.text_input("Was möchtest du TARS fragen?")

def build_prompt(question, humor, ehrlichkeit):
    return f"Du bist TARS, ein KI-Roboter aus dem Film Interstellar. Sprich Deutsch. Deine Antworten sind pragmatisch, manchmal sarkastisch, abhängig von der Humorstufe ({humor}%) und Ehrlichkeitsstufe ({ehrlichkeit}%). Antworte auf: '{question}'"

def speak(text):
    tts = gTTS(text, lang='de')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format="audio/mp3")

if user_input:
    prompt = build_prompt(user_input, humor, ehrlichkeit)
    with st.spinner("TARS denkt nach..."):
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            tars_reply = response.choices[0].message.content.strip()
            st.markdown(f"**TARS sagt:** {tars_reply}")
            speak(tars_reply)
        except Exception as e:
            st.error(f"Fehler bei der Kommunikation mit OpenAI: {e}")
