from object_detection import start_detection_thread, running_detection
from tts_module import speak
from voice_command import listen_command
from emergency_alert import send_sms
from gps_module import (
    start_navigation,
    get_current_location,
    find_nearest_place,
    get_directions,
    reverse_geocode,
)
import object_detection
import time


# 🌟 Wake word listener (runs only once)
def listen_for_wake_word():
    from voice_command import recognizer, sr  # imported here to avoid circular dependency
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎧 Say 'Smart Stick' to activate...")
        try:
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            if "smart stick" in command:
                print("✅ Wake word detected!")
                speak("Smart Stick Assistant Activated")
                return True
        except Exception:
            pass
    return False


if __name__ == "__main__":
    # 🌟 Wait for wake word ONCE
    activated = False
    while not activated:
        activated = listen_for_wake_word()

    # ✅ Once activated, continuously listen for commands
    speak("I am listening for your commands.")

    while True:
        cmd = listen_command()
        if not cmd:
            continue

        cmd = cmd.lower().strip()
        print(f"🗣️ Command received: {cmd}")

        # 🎯 Object detection
        if "front" in cmd or "ahead" in cmd or "object" in cmd:
            speak("Checking objects ahead.")
            start_detection_thread(speak_callback=speak)

        # 🚨 Emergency help
        elif "help" in cmd or "emergency" in cmd:
            location = get_current_location()
            send_sms(location)
            speak("Emergency alert sent.")

        # 📍 Current location
        elif "current" in cmd or "where am i" in cmd or "my location" in cmd:
            lat, lng = get_current_location()
            if lat and lng:
                address = reverse_geocode(lat, lng)
                if address:
                    speak(f"Your current location is {address}")
                    print(address)
                else:
                    speak(f"Your current location is latitude {lat}, longitude {lng}")
            else:
                speak("Sorry, I could not detect your location.")

        # 🚶 Nearest place
        elif "nearest" in cmd or "nearby" in cmd or "closest" in cmd:
            query = (
                cmd.replace("take me to", "")
                .replace("the", "")
                .replace("nearest", "")
                .replace("nearby", "")
                .replace("closest", "")
                .strip()
            )

            lat, lng = get_current_location()
            if not lat:
                speak("Sorry, I could not detect your location.")
                continue

            place = find_nearest_place(query, lat, lng)
            if place:
                place_name, dest_lat, dest_lng = place
                speak(f"Navigating to the nearest {query}: {place_name}")

                steps = get_directions(f"{lat},{lng}", f"{dest_lat},{dest_lng}")
                if steps:
                    for step in steps:
                        speak(step)
                else:
                    speak("Sorry, I could not get directions.")
            else:
                speak(f"Sorry, I could not find a {query} nearby.")

        # 🚶 Navigation - direct destination
        elif "take me to" in cmd:
            query = cmd.replace("take me to", "").strip()
            start_navigation(query)

        # 🛑 Exit
        elif "stop" in cmd or "exit" in cmd or "quit" in cmd:
            if object_detection.running_detection:
                object_detection.running_detection = False
                speak("Stopping object detection.")
            else:
                speak("Goodbye.")
                break

        else:
            speak("Sorry, I did not understand that command.")

        time.sleep(1)
