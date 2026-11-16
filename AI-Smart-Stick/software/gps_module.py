import requests
import pyttsx3
import speech_recognition as sr
from tts_module import speak

API_KEY = "AIzaSyCIh3_nVaLrH2Lkie17TmIEjiVme9lCYZM"  # 🔑 Replace with your Google Maps API key

# ----------------------------
# 🎤 Voice Recognition
# ----------------------------
def listen_command(prompt="Say something..."):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(prompt)
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=6)
        except sr.WaitTimeoutError:
            return None
    try:
        command = r.recognize_google(audio).lower()
        print("✅ Command recognized:", command)
        return command
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        print("⚠️ Speech recognition service error.")
        return None

# ----------------------------
# 🔊 Text-to-Speech
# ----------------------------
# def speak(text):
#     print("🔊", text)
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()

# ----------------------------
# 📍 Get Current Location (Google Geolocation API)
# ----------------------------
def get_current_location():
    try:
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={API_KEY}"
        response = requests.post(url).json()
        if "location" in response:
            lat = response["location"]["lat"]
            lng = response["location"]["lng"]
            return lat, lng
    except Exception as e:
        print("❌ Location error:", e)
    return None, None

# ----------------------------
# 📌 Geocode a Place Name
# ----------------------------
def geocode_place(place_name):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place_name}&key={API_KEY}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        formatted = response["results"][0]["formatted_address"]
        return location["lat"], location["lng"], formatted
    else:
        print("❌ Geocoding failed:", response.get("status"))
        return None, None, None

# ----------------------------
# 🏙️ Reverse Geocode
# ----------------------------
def reverse_geocode(lat, lng):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={API_KEY}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        return response["results"][0]["formatted_address"]
    return f"{lat},{lng}"

# ----------------------------
# 🌍 Get Directions
# ----------------------------
def get_directions(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={API_KEY}"
    response = requests.get(url).json()

    if response["status"] != "OK":
        print("❌ Directions API error:", response["status"])
        return None

    steps = []
    for leg in response["routes"][0]["legs"]:
        for step in leg["steps"]:
            instruction = step["html_instructions"]
            clean = (
                instruction.replace("<b>", "")
                .replace("</b>", "")
                .replace("<div style=\"font-size:0.9em\">", " ")
                .replace("</div>", "")
                .replace("/<wbr/>", " ")
                .replace("Rd", "Road")
            )
            steps.append(clean)
    return steps

# ----------------------------
# 🔎 Find Nearest Place
# ----------------------------
def find_nearest_place(place_type, lat, lng):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=3000&keyword={place_type}&key={API_KEY}"
    response = requests.get(url).json()

    if response["status"] == "OK" and response["results"]:
        place = response["results"][0]
        name = place["name"]
        dest_lat = place["geometry"]["location"]["lat"]
        dest_lng = place["geometry"]["location"]["lng"]
        return name, dest_lat, dest_lng
    else:
        print("❌ Nearby search error:", response.get("status"))
        return None, None, None

# ----------------------------
# 🚶 Start Navigation
# ----------------------------
def start_navigation(destination_query):
    # Step 1: Get current location
    lat, lng = get_current_location()
    if not lat or not lng:
        speak("Sorry, I could not detect your current location.")
        return
    origin = f"{lat},{lng}"

    # Normalize query
    query = destination_query.lower().strip()

    # Step 2: Handle "nearest / nearby / closest ..." queries
    if query.startswith("nearest") or query.startswith("the nearest"):
        place_type = query.replace("the nearest", "").replace("nearest", "").strip()

    elif query.startswith("closest"):
        place_type = query.replace("closest", "").strip()

    elif query.endswith("nearby"):
        place_type = query.replace("nearby", "").strip()

    else:
        place_type = None

    if place_type:
        name, dest_lat, dest_lng = find_nearest_place(place_type, lat, lng)
        if not name:
            speak(f"Sorry, I could not find a {place_type} nearby.")
            return
        speak(f"Starting navigation to the nearest {name}")
        destination = f"{dest_lat},{dest_lng}"

    # Step 3: Handle normal "take me to ..." queries
    else:
        dest_lat, dest_lng, formatted = geocode_place(query)
        if not dest_lat:
            speak(f"Sorry, I could not find {destination_query}.")
            return
        speak(f"Starting navigation to {formatted}")
        destination = f"{dest_lat},{dest_lng}"

    # Step 4: Get directions
    steps = get_directions(origin, destination)
    if not steps:
        speak("Sorry, I could not get directions.")
        return

    # Step 5: Read navigation step by step
    step_index = 0
    while step_index < len(steps):
        speak(steps[step_index])
        print("➡️", steps[step_index])

        command = listen_command("Say next for next step or stop to exit...")
        if command and "next" in command:
            step_index += 1
        elif command and "stop" in command:
            speak("Navigation stopped.")
            break
        else:
            speak("I didn't understand, please say next or stop.")

# ----------------------------
# Run Test
# ----------------------------
if __name__ == "__main__":
    destination = listen_command("Say your destination, like 'nearest hospital' or 'take me to MG Road'")
    if destination:
        if "take me to" in destination:
            query = destination.replace("take me to", "").strip()
            start_navigation(query)
        elif "nearest" in destination:
            start_navigation(destination)
        else:
            speak("Please say either 'take me to' or 'nearest' followed by your destination.")
