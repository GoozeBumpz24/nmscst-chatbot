from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import threading
import pyttsx3

app = Flask(__name__)
CORS(app)

# Text-to-Speech Engine Initialization
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 0.9)

# In-memory room data (extend this data with latitude and longitude for demo purposes)
rooms = {
    "101": {
        "room_name": "101",
        "building": "Main Building",
        "directions": "Take the stairs to the first floor, turn left.",
        "image": "static/uploads/room101.jpg",
        "latitude": 14.5995,
        "longitude": 120.9842
    },
    "library": {
        "room_name": "Library",
        "building": "Academic Building",
        "directions": "Walk straight to the end of the hallway on the ground floor.",
        "image": "static/uploads/library.jpg",
        "latitude": 14.5999,
        "longitude": 120.9839
    }
}

# Helper function for text-to-speech
def speak(text):
    """Function to make the chatbot speak a response in a separate thread."""
    def speak_in_thread():
        tts_engine.say(text)
        tts_engine.runAndWait()

    threading.Thread(target=speak_in_thread).start()

# Function to get room directions with Google Maps link
def get_room_directions(room_name):
    room = rooms.get(room_name.lower())  # Case-insensitive search
    if room:
        map_url = f"https://www.google.com/maps/search/?api=1&query={room['latitude']},{room['longitude']}"
        return (f"Room {room['room_name']} is in {room['building']}. Directions: {room['directions']}. "
                f"<a href='{map_url}' target='_blank'>View on Google Maps</a>. "
                f"<img src='/{room['image']}' alt='Room Image' style='width: 200px;'>")
    else:
        return "Sorry, I couldn't find that room. Please check the room name or number."

# Chatbot API route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    question = data.get("message", "").strip().lower()

    if "where is" in question:
        room_name = question.replace("where is", "").strip()
        response = get_room_directions(room_name)
    else:
        response = "I'm sorry, I didn't understand that. Can you rephrase?"

    speak(response)
    return jsonify({"response": response})

# Serve the home page
@app.route('/')
def home():
    return render_template('index.html')

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
