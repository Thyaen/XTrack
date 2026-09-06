#!/usr/bin/python3

import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set properties (optional: adjust volume and speech rate)
engine.setProperty('volume', 0.9)  # Volume 0-1
engine.setProperty('rate', 150)    # Speech rate

# Say "Hello World"
engine.say("Hello World")

# Play the speech through the USB speaker
engine.runAndWait()