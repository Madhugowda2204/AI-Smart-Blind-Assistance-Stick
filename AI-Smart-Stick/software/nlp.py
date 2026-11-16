import random
import os
from gtts import gTTS
import speech_recognition as sr
from gensim.downloader import load
from gensim.models import KeyedVectors
import numpy as np

# Load pre-trained Google News Word2Vec (if available)
# model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin.gz', binary=True)


# Load Word2Vec model
print("Loading NLP model...")
model = load("glove-wiki-gigaword-50")

# Speech-to-text
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except:
        print("❌ Could not recognize speech.")
        return ""

# Text-to-speech
def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("start response.mp3") # Windows

#gps
def classify_intent(user_query):
    user_query = user_query.lower()
    if "where am i" in user_query:
        return "location"
    elif "guide me" in user_query or "navigate" in user_query or "take me" in user_query:
        return "navigation"
    elif "what is in front" in user_query or "what’s in front" in user_query:
        return "object_detection"
    else:
        return "unknown"
    
# Intents
intents = {
    "front": ["front", "ahead", "obstacle"],
    "left": ["left", "side"],
    "right": ["right", "side"],
    "distance": ["distance", "far", "near"]
}

def get_intent(question):
    words = question.lower().split()
    best_intent = None
    best_score = -1
    
    for intent, keywords in intents.items():
        for kw in keywords:
            for w in words:
                if w in model.key_to_index and kw in model.key_to_index:
                    score = model.similarity(w, kw)
                    if score > best_score:
                        best_score = score
                        best_intent = intent
    return best_intent

# Fake distance generator
def get_fake_distance():
    return random.randint(10, 200)  # cm

# Main loop
while True:
    question = listen()
    if question == "":
        continue

    intent = get_intent(question)

    if intent in ["front", "left", "right"]:
        dist = get_fake_distance()
        response = f"There is an obstacle {dist} cm to your {intent}."
    else:
        response = "Sorry, I didn’t understand your question."

    print("Bot:", response)
    speak(response)
