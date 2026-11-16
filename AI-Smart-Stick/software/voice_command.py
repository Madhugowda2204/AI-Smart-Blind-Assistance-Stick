import speech_recognition as sr
import time

recognizer = sr.Recognizer()
WAKE_WORD = "smart stick"  # You can change this

def listen_command(timeout=7, phrase_time_limit=7):
    """
    Listen to the microphone and return recognized text (lowercase).
    Returns None if speech is not understood.
    """
    with sr.Microphone() as source:
        print("🎤 Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except Exception:
            return None

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"✅ Command recognized: {command}")
        return command
    except sr.UnknownValueError:
        print("❌ Could not understand the command")
        return None
    except sr.RequestError:
        print("⚠️ Speech recognition service error")
        return None


def listen_for_wake_word():
    """
    Continuously listen for the wake word ("smart stick") and return True when heard.
    """
    with sr.Microphone() as source:
        print("👂 Waiting for wake word...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
            command = recognizer.recognize_google(audio).lower()
            print(f"Heard: {command}")
            if WAKE_WORD in command:
                print("🟢 Wake word detected!")
                return True
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print("⚠️ Speech recognition service error")

    return False


if __name__ == "__main__":
    while True:
        if listen_for_wake_word():
            print("🎙️ Speak your command now...")
            command = listen_command()
            if command:
                if "stop" in command:
                    print("🛑 Stopping voice control.")
                    break
                else:
                    print(f"🧠 Processing command: {command}")
            else:
                print("⚠️ No command detected.")
            time.sleep(1)
