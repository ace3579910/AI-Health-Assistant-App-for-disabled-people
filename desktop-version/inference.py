# single_capture_inference.py
import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import mediapipe as mp
import time

# ==========================
# CONFIG
# ==========================
SEQUENCE_LENGTH = 60
SYMPTOMS = [
    "fever", "sore_throat", "cough", "low_back_pain", "nausea", "dizziness",
    # "headache_forehead", "headache_temple",
    # "nasal_congestion",
    # "chest_pain_center", "shortness_of_breath",
    # "abdominal_pain",
    # "knee_pain", "chills", "fatigue",
]

# ==========================
# LOAD MODEL & SCALER
# ==========================
model = load_model("sign_symptom_model.h5")
scaler = StandardScaler()  # Replace with saved scaler if available

# ==========================
# MEDIA PIPE SETUP
# ==========================
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

def extract_landmarks(results):
    pose = np.array([[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*3)
    lh = np.array([[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

def preprocess_sequence(sequence):
    X_seq = np.array(sequence).reshape(SEQUENCE_LENGTH, -1)
    X_scaled = scaler.fit_transform(X_seq)  # Use transform if saved scaler
    return X_scaled.reshape(1, SEQUENCE_LENGTH, X_scaled.shape[1])

# ==========================
# STREAMLIT UI
# ==========================
st.title("Sign Language Symptom Recognition")
st.write("Click 'Capture Gesture' to record 60 frames and predict the symptom.")

if st.button("Capture Gesture"):
    cap = cv2.VideoCapture(0)
    sequence = []
    stframe = st.empty()
    progress_bar = st.progress(0)  # Initialize progress bar
    
    with mp_holistic.Holistic(static_image_mode=False) as holistic:
        frames_captured = 0
        while frames_captured < SEQUENCE_LENGTH:
            ret, frame = cap.read()
            if not ret:
                st.warning("Camera not found!")
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame_rgb)
            landmarks = extract_landmarks(results)
            sequence.append(landmarks)
            
            # Draw landmarks
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            
            stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
            
            frames_captured += 1
            progress_bar.progress(frames_captured / SEQUENCE_LENGTH)  # Update progress
            time.sleep(0.05)  # ~20 FPS

    cap.release()
    
    if len(sequence) == SEQUENCE_LENGTH:
        X_input = preprocess_sequence(sequence)
        pred = model.predict(X_input)
        pred_class = SYMPTOMS[np.argmax(pred)]
        st.success(f"Predicted Symptom: **{pred_class}**")
        st.bar_chart(pred.flatten())
    else:
        st.error("Failed to capture enough frames. Try again.")
