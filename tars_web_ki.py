import streamlit as st import openai import requests import tempfile import os from streamlit_webrtc import webrtc_streamer, AudioProcessorBase import speech_recognition as sr

OpenAI und ElevenLabs API Keys aus Streamlit Secrets

openai.api_key = st.secrets["openai_key"] elevenlabs_api_key = st.secrets["eleven_key"]

Web-Oberfläche

st.set_page_config(page_title="TARS KI", layout="centered") st.title("TARS - Deine deutschsprachige KI") st.markdown("Bereit für den nächsten Befehl, Ramon.")

Einstellbare Werte

humor = st.slider("Humorstufe", 0, 100, 20) ehrlichkeit = st.slider("Ehrlichkeitsstufe", 0, 100, 100)

Sprachaufnahme

st.markdown("Sprich deine Frage:") uploaded_audio = st.audio_recorder(label="Sprich jetzt", sample_rate=44100)

user_input = "" if uploaded_audio: with open("temp.wav", "wb") as f: f.write(uploaded_audio.getbuffer()) r = sr.Recognizer() with sr.AudioFile("temp.wav") as source: audio = r.record(source) try: user_input = r.recognize_google(audio, language="de-DE") st.success(f"Verstanden: {user_input}") except: st.error("Konnte dich nicht verstehen. Bitte nochmal versuchen.")

Fallback: manuelle Texteingabe

if not user_input: user_input = st.text_input("Oder gib deine Frage manuell ein:")

Prompt-Builder

def build_prompt(question, humor, ehrlichkeit): return f"Du bist TARS, ein KI-Roboter aus dem Film Interstellar. Sprich Deutsch. Deine Antworten sind pragmatisch, manchmal sarkastisch, abhängig von der Humorstufe ({humor}%) und Ehrlichkeitsstufe ({ehrlichkeit}%). Antworte auf: '{question}'"

Sprachausgabe über ElevenLabs mit der angegebenen Voice-ID + Autoplay

def speak_with_elevenlabs(text): voice_id = "FTNCalFNG5bRnkkaP5Ug"  # Deine gewünschte deutsche Stimme url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" headers = { "xi-api-key": elevenlabs_api_key, "Content-Type": "application/json" } data = { "text": text, "model_id": "eleven_multilingual_v2", "voice_settings": { "stability": 0.6, "similarity_boost": 0.7 } } response = requests.post(url, headers=headers, json=data) if response.status_code == 200: with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp: fp.write(response.content) audio_path = fp.name st.markdown( f"<audio autoplay src='data:audio/mp3;base64,{response.content.encode('base64').decode()}'></audio>", unsafe_allow_html=True ) else: st.error("Fehler bei der Sprachausgabe von ElevenLabs")

Antwort von GPT holen und sprechen

if user_input: prompt = build_prompt(user_input, humor, ehrlichkeit) with st.spinner("TARS denkt nach..."): try: response = openai.chat.completions.create( model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}] ) tars_reply = response.choices[0].message.content.strip() st.markdown(f"TARS sagt: {tars_reply}") speak_with_elevenlabs(tars_reply) except Exception as e: st.error(f"Fehler bei OpenAI oder ElevenLabs: {e}")

