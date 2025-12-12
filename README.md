
This project contains two versions of the same idea:
an AI-based health assistant that can help users (especially elderly and disabled people) check symptoms and get basic suggestions.
One version is meant for laptops/desktops, and the other runs on a Raspberry Pi with sensors.

The goal is to make health monitoring more accessible by combining simple inputs, hand-sign recognition, and basic sensor readings.

This repository contains two separate builds:  
  1.Desktop Version  
  2.Raspberry Pi Version  
Each version is optimized for the device it runs on.

**1. Desktop version**  

The desktop version contains a custom hand-sign dataset, AI-based prediction, and tools to add your own symptoms.
Clone the desktop version using commands:
  ```bash
  git clone https://github.com/ace3579910/AI-Health-Assistant-App-for-disabled-people.git
  ```
Move into the desktop-version folder:
  ```bash
  cd AI-Health-Assistant-App-for-disabled-people/desktop-version
  ```
Install the required libraries for the desktop version using the command below.  
This will set up all dependencies needed for gesture capture, inference, and the AI assistant.
```bash
pip install -r requirements-desktop.txt
```

1. **gesture_data:** Custom Dataset (Hand Sign Detection)
This dataset includes hand-sign images for the following symptoms:  

&nbsp;&nbsp;&nbsp; -cough  
  
&nbsp;&nbsp;&nbsp; -dizziness  
  
&nbsp;&nbsp;&nbsp; -fever  
  
&nbsp;&nbsp;&nbsp; -low_back_pain  
  
&nbsp;&nbsp;&nbsp; -nausea  
  
&nbsp;&nbsp;&nbsp; -sore_throat

These datasets are used for training models that convert hand gestures into symptom text.

2. **Gemini_API_ADv.py**
This is the main assistant interface.
It lets you:  

 &nbsp;&nbsp;&nbsp; -type or speak symptoms  
    
  &nbsp;&nbsp;&nbsp; -enter temperature, SpO₂, and heart rate  
  
 &nbsp;&nbsp;&nbsp; -get a simplified health explanation and suggested basic care  
  
 &nbsp;&nbsp;&nbsp; -have the results read aloud using text-to-speech  

The app also tries to understand vitals if you speak them aloud (e.g., “temperature 100 point 4, SpO₂ 94, heart rate 96”).

Run Gemini_API_ADv.py
```bash
python -m streamlit run Gemini_API_ADv.py
```
3. **code2.py:** Gesture Recording Tool
This tool records 60-frame sequences of your hand/pose movements using Mediapipe.
You can:  

&nbsp;&nbsp;&nbsp;  i. pick a symptom from the list  
  
&nbsp;&nbsp;&nbsp;  ii. record a gesture  

  &nbsp;&nbsp;&nbsp;iii. save the frames as .npy files
These files form the dataset used for training or testing gesture recognition.

Run code2.py
```bash
python -m streamlit run code2.py
```
4. inference.py

This script is used to run gesture-based symptom recognition after you already have a trained model.
It takes a short live camera recording, extracts the pose and hand landmarks, and then predicts which symptom gesture you performed. The predicted label can then be passed into the main health assistant.

This file is mainly meant for testing the model or quickly checking how well your gestures are being recognized.

Run inference.py
```bash
python -m streamlit run inference.py
```

**2. Raspberry Pi Version**
This version is meant to run on a Raspberry Pi using Linux.  

It uses the DS18B20 temperature sensor along with a lightweight Streamlit-based health assistant.

The Pi setup requires enabling the 1-Wire interface, creating a virtual environment, and running both Python scripts separately.  
The DS18B20 temperature script does not require additional Python packages.
It accesses sensor readings directly from the Linux system path: /sys/bus/w1/devices/  
**Enable DS18B20 Sensor on Raspberry Pi**
Run the following commands once to enable the 1-Wire interface:  
```bash
echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt
```
```bash
sudo modprobe w1-gpio
```
```bash
sudo modprobe w1-therm
```

  ```bash
sudo reboot
```

  After reboot, verify that the sensor is detected:  
```bash
ls /sys/bus/w1/devices/
```
A folder starting with 28- should appear if the sensor is connected.  
Now,
Clone the Repository  
```bash
git clone https://github.com/ace3579910/AI-Health-Assistant-App-for-disabled-people.git
```
Navigate to the folder
```bash
cd AI-Health-Assistant-App-for-disabled-people/Raspberry-version
```
Now setup Virtual Environment Setup (venv)  
venv is a virtual environment keeps all the Python packages for this project isolated from the system Python installation. This prevents version conflicts, makes the project easier to manage, and ensures that the desktop and Raspberry Pi versions each use the correct dependencies without affecting other programs on the device.  
```bash
python3 -m venv venv 
```
It creates a new virtual environment folder named venv
```bash
source venv/bin/activate
```
Install required packages:  
```bash
pip install --upgrade pip
pip install -r requirements-rpi.txt
```
**1. Running the DS18B20 Temperature Reader:**  
Connect the following pins  
<img width="235" height="215" alt="image" src="https://github.com/user-attachments/assets/9332d480-9314-4899-983b-dadded720a11" />  
&nbsp;&nbsp;&nbsp;i. VCC to 3.3V (Pin 1)  
&nbsp;&nbsp;&nbsp;ii. GND to GND (Pin 6)  
&nbsp;&nbsp;&nbsp;iii. DQ (Data) to GPIO4 (Pin 7)    

A 4.7kΩ pull-up resistor must be placed between DQ (Data) and 3.3V  
This resistor is required for stable 1-Wire communication.  
Run the following command:
```bash
python3 DS18B20.py
```
Press Ctrl + C to exit.  

**2. Running the AI Health Assistant on Raspberry Pi:**  
The Raspberry Pi assistant accepts manual inputs such as symptoms, temperature, SpO₂, and heart rate.

Run the application:  
```bash
python -m streamlit run ai_health_assistant_app.py
```
After running the command, open the app in your browser. If you are running Streamlit on your own computer, use http://localhost:8501. If you are running it on a Raspberry Pi through PuTTY or SSH, open the Network URL shown in the terminal (for example, http://<pi-ip>:8501) from any device on the same network.

Now to deactivate venv , type the following command:
```bash
deactivate
```
