import threading
import streamlit as st
from google import genai
import speech_recognition as sr
import pyttsx3
import re
import time

# =============================
# Initialization
# =============================
client = genai.Client(api_key="AIzaSyBmRet1PvcdC-_omO4jh_j4kSHQTU3oKKEz")
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

# =============================
# Helper Functions
# =============================
import threading

def speak_text(text):
    """Thread-safe text-to-speech function."""
    def _speak():
        try:
            local_engine = pyttsx3.init()
            local_engine.setProperty('rate', 170)
            local_engine.setProperty('volume', 1.0)
            local_engine.say(text)
            local_engine.runAndWait()
            local_engine.stop()
        except RuntimeError:
            pass  # silently ignore race condition errors

    # run TTS in a separate thread
    threading.Thread(target=_speak, daemon=True).start()

def recognize_speech(prompt="Listening...", time_limit=6):
    """Capture voice input."""
    with sr.Microphone() as source:
        st.info(f"🎤 {prompt}")
        audio = recognizer.listen(source, phrase_time_limit=time_limit)
    try:
        text = recognizer.recognize_google(audio)
        st.success(f"🗣️ Heard: {text}")
        return text.lower()
    except sr.UnknownValueError:
        st.warning("❌ Couldn't understand speech.")
        return ""
    except sr.RequestError:
        st.error("⚠️ Speech service unavailable.")
        return ""

def parse_vitals_from_text(text):
    """Extract temperature, SpO2, and heart rate from voice."""
    temp_f, spo2, hr = None, None, None
    temp_match = re.search(r"(\d+(?:\.\d+)?)\s*(f|fahrenheit|c|celsius|degrees)?", text)
    if temp_match:
        val, unit = temp_match.groups()
        val = float(val)
        if unit in ["c", "celsius"]:
            temp_f = round((val * 9 / 5) + 32, 1)
        elif unit in ["f", "fahrenheit"] or (val >= 80 and val <= 110):
            temp_f = round(val, 1)
        elif 30 <= val <= 45:
            temp_f = round((val * 9 / 5) + 32, 1)

    spo2_match = re.search(r"(\d{2,3})\s*%|spo2\s*(\d{2,3})", text)
    if spo2_match:
        spo2 = int(spo2_match.group(1) or spo2_match.group(2))

    hr_match = re.search(r"(heart rate|pulse)\s*(\d{2,3})|(\d{2,3})\s*bpm", text)
    if hr_match:
        hr = int(hr_match.group(2) or hr_match.group(3))

    return temp_f, spo2, hr

# =============================
# Streamlit UI (same layout)
# =============================
st.set_page_config(page_title="🩺 AI Health Assistant", layout="centered")

st.title("🩺 AI Health Assistant")
st.markdown("Your friendly, accessibility-focused AI health companion powered by Gemini.")

with st.form("health_form"):
    symptoms = st.text_area(
        "Describe your symptoms (comma separated):",
        placeholder="e.g., fever, sore throat, cold, cough"
    )
    temperature_f = st.number_input("Temperature (°F):", 80.0, 110.0, 98.6, 0.1)
    spo2 = st.number_input("SpO₂ Level (%):", 70, 100, 95, 1)
    heart_rate = st.number_input("Heart Rate (bpm):", 40, 200, 98, 1)

    if st.form_submit_button("🎤 Speak Symptoms"):
        voice_input = recognize_speech("Please describe your symptoms clearly.")
        if voice_input:
            symptoms = voice_input
            st.session_state["symptoms"] = voice_input

    submitted = st.form_submit_button("Analyze")

if "symptoms" in st.session_state and not submitted:
    symptoms = st.session_state["symptoms"]

# =============================
# Voice Command Interface
# =============================
st.markdown("---")
st.markdown("🎙️ Voice Commands:")
st.markdown("- **start recording** → record symptoms")
st.markdown("- **set vitals** → input temperature, SpO₂, and heart rate by voice")
st.markdown("- **start analysis** → begin health check")
st.markdown("- **summary / full** → choose what to hear")

command = recognize_speech("Say a command (start recording, set vitals, or start analysis)", 6)

if "record" in command or "symptom" in command:
    voice_symptoms = recognize_speech("Please tell me your symptoms clearly.", 10)
    if voice_symptoms:
        symptoms = voice_symptoms
        st.session_state["symptoms"] = voice_symptoms
        speak_text(f"Got it. You said: {symptoms}. Say 'set vitals' or 'start analysis'.")

elif "vital" in command or "set vital" in command:
    vital_text = recognize_speech("Please say your vitals. For example: temperature 100.4, SpO2 94, heart rate 96.", 10)
    temp_parsed, spo2_parsed, hr_parsed = parse_vitals_from_text(vital_text)
    if temp_parsed:
        temperature_f = temp_parsed
    if spo2_parsed:
        spo2 = spo2_parsed
    if hr_parsed:
        heart_rate = hr_parsed
    st.session_state["temp"] = temperature_f
    st.session_state["spo2"] = spo2
    st.session_state["hr"] = heart_rate
    speak_text(f"Vitals updated. Temperature {temperature_f} Fahrenheit, SpO2 {spo2} percent, heart rate {heart_rate} bpm.")

elif "analysis" in command:
    submitted = True
    speak_text("Starting your analysis now.")

# =============================
# Health Analysis (same logic)
# =============================
if submitted:
    vitals_section = f"""
### 🩺 Health Analysis Result
**Symptoms Detected:** {symptoms}  
**Temperature:** {temperature_f:.1f}°F  
**SpO₂:** {spo2}%  
**Heart Rate:** {heart_rate} bpm  
"""

    if temperature_f > 102 or spo2 < 92 or heart_rate > 120:
        severity_level = "🔴 Urgent – Seek medical attention soon"
        severity_note = "The patient shows potentially serious symptoms. Prioritize urgent care advice."
        banner_color = "#FF4C4C"
    elif temperature_f >= 99.5 or spo2 < 95 or heart_rate > 100:
        severity_level = "🟠 Moderate – Care and monitor your symptoms"
        severity_note = "The patient shows moderate symptoms. Give careful guidance, symptom-specific advice, and suggested timelines."
        banner_color = "#FFA500"
    else:
        severity_level = "🟢 Mild – Home remedies and rest should help"
        severity_note = "The patient shows mild symptoms. Give gentle, reassuring home care advice, symptom-specific remedies, and timelines."
        banner_color = "#4CAF50"

    st.markdown(f"""
<div style="background-color:{banner_color}; padding: 10px; border-radius:5px;">
<h3 style="color:white; margin:0;">⚠️ Severity Level: {severity_level}</h3>
</div>
""", unsafe_allow_html=True)

    urgent_symptoms = []
    if temperature_f > 102:
        urgent_symptoms.append("High fever (>102°F)")
    if spo2 < 92:
        urgent_symptoms.append("Low oxygen (SpO₂ < 92%)")
    if heart_rate > 120:
        urgent_symptoms.append("Rapid heart rate (>120 bpm)")
    triage_note = "🚨 **Immediate Concern:** " + ", ".join(urgent_symptoms) if urgent_symptoms else "✅ No critical symptoms detected. Follow care advice below."
    st.markdown(f"**Clinical Triage:** {triage_note}")

    # Gemini Prompt
    prompt = f"""
You are a warm, caring, and knowledgeable AI health assistant.
{severity_note}

Based on the given symptoms and vitals, respond in a short, empathetic, and clear manner.

Include:
💡 Likely cause of the symptoms  
🍵 Home remedies and easy relief options  
💊 Basic over-the-counter medicines (like Paracetamol, Cetirizine)  
⏱️ Advice on monitoring and when to seek a doctor  
⚕️ End with a friendly disclaimer.

Symptoms: {symptoms}
Temperature: {temperature_f:.1f}°F
SpO₂: {spo2}%
Heart Rate: {heart_rate} bpm
Urgent Symptoms: {', '.join(urgent_symptoms) if urgent_symptoms else 'None'}
"""

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        health_advice = response.text.strip()
    except Exception as e:
        health_advice = f"⚠️ Error calling Gemini API: {str(e)}"

    st.markdown(vitals_section)
    st.markdown("---")
    st.subheader("💬 Suggested Care, Remedies & Timelines")
    st.markdown(health_advice)
    st.markdown("---")
    st.caption("⚕️ *Note: This is not a substitute for professional medical advice. Always consult a doctor if your condition worsens.*")

    # Generate short summary
    summary_prompt = f"Summarize this advice in 3 short bullet points (severity, remedies, doctor note). Text: {health_advice}"
    try:
        summary_resp = client.models.generate_content(model="gemini-2.5-flash", contents=summary_prompt)
        short_summary = summary_resp.text.strip()
    except Exception:
        short_summary = "Summary unavailable. Please follow the advice carefully."

    # TTS options
    st.markdown("### 🔊 Audio Assistance")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 Quick Summary Readout"):
            speak_text(short_summary)
    with col2:
        if st.button("📖 Full Readout"):
            speak_text(health_advice)

    # Voice playback
    speak_text("Would you like me to read the summary or the full response?")
    time.sleep(1.2)
    playback_cmd = recognize_speech("Say summary or full.", 4)
    if "summary" in playback_cmd:
        speak_text(short_summary)
    elif "full" in playback_cmd:
        speak_text(health_advice)
    else:
        speak_text(short_summary)
