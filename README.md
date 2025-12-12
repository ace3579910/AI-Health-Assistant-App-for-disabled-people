
This project contains two versions of the same idea:
an AI-based health assistant that can help users (especially elderly and disabled people) check symptoms and get basic suggestions.
One version is meant for laptops/desktops, and the other runs on a Raspberry Pi with sensors.

The goal is to make health monitoring more accessible by combining simple inputs, hand-sign recognition, and basic sensor readings.

This repository contains two separate builds:  
  1.Desktop Version  
  2.Raspberry Pi Version  
Each version is optimized for the device it runs on.

**Desktop version**
The desktop version contains a custom hand-sign dataset, AI-based prediction, and tools to add your own symptoms.
Clone the desktop version using commands:
  ```bash
  git clone https://github.com/ace3579910/assistive-health-assistant.git
  ```

Install the required libraries for the desktop version using the command below.  
This will set up all dependencies needed for gesture capture, inference, and the AI assistant.
```bash
pip install -r requirements-desktop.txt
```

1.**gesture_data:** Custom Dataset (Hand Sign Detection)
This dataset includes hand-sign images for the following symptoms:  

&nbsp;&nbsp;&nbsp;-cough  
  
&nbsp;&nbsp;&nbsp;-dizziness  
  
 &nbsp;&nbsp;&nbsp; -fever  
  
&nbsp;&nbsp;&nbsp;  -low_back_pain  
  
&nbsp;&nbsp;&nbsp; -nausea  
  
 &nbsp;&nbsp;&nbsp;-sore_throat

These datasets are used for training models that convert hand gestures into symptom text.

2.**Gemini_API_ADv.py**
This is the main assistant interface.
It lets you:  
```
  -type or speak symptoms  
  
  -enter temperature, SpO₂, and heart rate  
  
  -get a simplified health explanation and suggested basic care  
  
  -have the results read aloud using text-to-speech  
```
The app also tries to understand vitals if you speak them aloud (e.g., “temperature 100 point 4, SpO2 94, heart rate 96”).

3.**code2.py:** Gesture Recording Tool
This tool records 60-frame sequences of your hand/pose movements using Mediapipe.
You can:  
```
  i. pick a symptom from the list  
  
  ii. record a gesture  
 ``` 
  iii. save the frames as .npy files
These files form the dataset used for training or testing gesture recognition.

3. inference.py

This file runs a trained model to convert a gesture (captured from camera) into a text label.
Whatever it predicts can be fed into the main assistant.

