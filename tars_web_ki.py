import streamlit as st
import openai
import requests
import base64

# API-Schlüssel aus Streamlit Secrets
openai.api_key = st.secrets["openai_key"]
elevenlabs_api_key = st.secrets["eleven_key"]

# Session-State Initialisierung
if "antwort_laeuft" not in st.session_state:
    st.session_state["antwort_laeuft"] = False
if "letzte_antwort" not in st.session_state:
    st.session_state["letzte_antwort"] = ""
if "frage_erlaubt" not in st.session_state:
    st.session_state["frage_erlaubt"] = True

# Streamlit-Seitenkonfiguration
st.set_page_config(page_title="TARS KI", layout="centered")
st.title("TARS - Deine deutschsprachige KI")

# TARS Gesicht anzeigen
st.markdown("""
<style>
.tars-face {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 20px 0;
}
.tars-unit {
    width: 100px;
    height: 150px;
    background: #222;
    border: 2px solid #666;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 0 20px #000;
}
.tars-eyes {
    display: flex;
    gap: 10px;
}
.tars-eye {
    width: 20px;
    height: 20px;
    background: #333;
    border-radius: 50%;
    transition: background 0.3s ease-in-out;
}
.tars-eye.blink {
    background: #0ff;
    box-shadow: 0 0 10px #0ff;
}
</style>
<div class="tars-face">
  <div class="tars-unit">
    <div class="tars-eyes">
      <div class="tars-eye" id="eye1"></div>
      <div class="tars-eye" id="eye2"></div>
    </div>
  </div>
</div>
<script>
function blinkEyes() {
  const e1 = document.getElementById("eye1");
  const e2 = document.getElementById("eye2");
  if (!e1 || !e2) return;
  e1.classList.add("blink");
  e2.classList.add("blink");
  setTimeout(() => {
    e1.classList.remove("blink");
    e2.classList.remove("blink");
  }, 1500);
}
</script>
""", unsafe_allow_html=True)

# Regler (werden bei Antwort gesperrt)
humor = st.slider("Humorstufe", 0, 100, 20, disabled=st.session_state["antwort_laeuft"])
ehrlichkeit = st.slider("Ehrlichkeitsstufe", 0, 100, 100, disabled=st.session_state["antwort_laeuft"])

# Eingabe mit Button-Steuerung
user_input = None
if st.session_state["frage_erlaubt"] and not st.session_state["antwort_laeuft"]:
    user_input = st.text_input("Was möchtest du TARS fragen?")

# Prompt-Vorbereitung
def build_prompt(question, humor, ehrlichkeit):
    return (
        f"Du bist TARS, ein KI-Roboter aus dem Film Interstellar. "
        f"Sprich Deutsch. Deine Antworten sind pragmatisch, manchmal sarkastisch, "
        f"abhängig von der Humorstufe ({humor}%) und Ehrlichkeitsstufe ({ehrlichkeit}%). "
        f"Antworte auf: '{question}'"
    )

# Sprachausgabe mit minimalistischem Player
def speak_with_elevenlabs(text):
    voice_id = "FTNCalFNG5bRnkkaP5Ug"
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
        st.markdown("<script>blinkEyes();</script>", unsafe_allow_html=True)
        audio_html = f"""
            <audio id="tarsAudio" autoplay>
              <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            <div style="margin-top: 10px;">
              <button onclick="document.getElementById('tarsAudio').paused ? document.getElementById('tarsAudio').play() : document.getElementById('tarsAudio').pause()">⏯️ Abspielen / Pause</button>
              <button onclick="document.getElementById('tarsAudio').currentTime = 0; document.getElementById('tarsAudio').play()">🔁 Wiederholen</button>
            </div>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.error(f"Fehler bei der Sprachausgabe von ElevenLabs: {response.status_code} – {response.text}")

# Antwortverarbeitung
if user_input:
    st.session_state["antwort_laeuft"] = True
    st.session_state["frage_erlaubt"] = False
    prompt = build_prompt(user_input, humor, ehrlichkeit)
    with st.spinner("TARS denkt nach..."):
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            tars_reply = response.choices[0].message.content.strip()
            st.session_state["letzte_antwort"] = tars_reply
            st.markdown(f"**TARS sagt:**")
            st.markdown(tars_reply)
            speak_with_elevenlabs(tars_reply)
        except Exception as e:
            st.error(f"Fehler bei OpenAI oder ElevenLabs: {e}")
    st.session_state["antwort_laeuft"] = False

# Neue Frage starten
if not st.session_state["frage_erlaubt"] and not st.session_state["antwort_laeuft"]:
    if st.button("Neue Frage stellen"):
        st.session_state["frage_erlaubt"] = True
