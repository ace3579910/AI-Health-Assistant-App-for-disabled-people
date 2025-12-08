import streamlit as st
import cv2
import numpy as np
import os
import mediapipe as mp
from datetime import datetime

# ==== CONFIG ====
DATA_PATH = "gesture_data"
SEQUENCE_LENGTH = 60  # frames per sequence
SYMPTOMS = [
    "fever", "sore_throat", "cough", "low_back_pain", "nausea", "dizziness",
    # "headache_forehead", "headache_temple",
    # "nasal_congestion",
    # "chest_pain_center", "shortness_of_breath",
    # "abdominal_pain",
    # "knee_pain", "chills", "fatigue",
]

# Create folders
os.makedirs(DATA_PATH, exist_ok=True)
for s in SYMPTOMS:
    os.makedirs(os.path.join(DATA_PATH, s), exist_ok=True)

# Mediapipe init
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*3)
    left_hand = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    right_hand = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    return np.concatenate([pose, left_hand, right_hand, face])

# ==== STREAMLIT UI ====
st.title("🎥 Symptom Gesture Data Capture")
st.write("Capture **60-frame sequences** for each symptom sign.")

selected_symptom = st.selectbox("Select Symptom", SYMPTOMS)
record_button = st.button("🎬 Record Gesture")

FRAME_WINDOW = st.image([])

if record_button:
    cap = cv2.VideoCapture(0)
    sequence = []
    st.info(f"Recording for: {selected_symptom} — Please perform the gesture!")

    # Add progress bar and status text
    progress_bar = st.progress(0)
    status_text = st.empty()

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while len(sequence) < SEQUENCE_LENGTH:
            ret, frame = cap.read()
            if not ret:
                st.error("Camera not detected.")
                break

            # Process frame
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)

            # Draw landmarks
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            # Extract & store keypoints
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)

            # Update Streamlit elements
            FRAME_WINDOW.image(image, channels="BGR", use_container_width=True)
            progress = len(sequence) / SEQUENCE_LENGTH
            progress_bar.progress(progress)
            status_text.text(f"📸 Capturing frame {len(sequence)}/{SEQUENCE_LENGTH}")

        cap.release()

    # Save sequence
    if len(sequence) == SEQUENCE_LENGTH:
        sequence = np.array(sequence)
        filename = os.path.join(DATA_PATH, selected_symptom, f"{selected_symptom}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.npy")
        np.save(filename, sequence)
        st.success(f"✅ Saved: {filename}")
        status_text.text("✅ Capture Complete!")
        progress_bar.progress(1.0)
