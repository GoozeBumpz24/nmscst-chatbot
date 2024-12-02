from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import datetime
import webbrowser
import pyttsx3
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Text-to-Speech Engine Initialization
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 0.9)

# Configuration for uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory room data
rooms = {}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to handle Text-to-Speech (TTS)
def speak(text):
    """Function to make the chatbot speak a response in a separate thread."""
    def speak_in_thread():
        tts_engine.say(text)
        tts_engine.runAndWait()

    threading.Thread(target=speak_in_thread).start()

# Chatbot response generation
def generate_response(question):
    question = question.lower()

    if "date" in question:
        now = datetime.datetime.now()
        response = f"Today's date is {now.strftime('%A, %B %d, %Y')}."
    elif question.startswith("open "):
        url = question[5:].strip()
        webbrowser.open(url)
        response = f"Opening {url} in your browser."
    elif "advice" in question:
        response = "Remember to take breaks and stay hydrated while you work!"
    elif "hello" in question or "hi" in question:
        response = "Hello! How can I assist you today?"
    elif "how are you" in question:
        response = "I'm just a program, but thanks for asking! How can I help you?"
    elif "bye" in question or "goodbye" in question:
        response = "Goodbye! Have a great day!"
    elif "your name" in question:
        response = "I'm your friendly chatbot. What's your name?"
    elif "where is" in question:
        room_name = question.replace("where is", "").strip()
        response = get_room_directions(room_name)
    else:
        response = "I'm sorry, I didn't understand that. Can you rephrase?"

    speak(response)
    return response

# Route to get directions for a specific room
def get_room_directions(room_name):
    room = rooms.get(room_name.lower())  # Ensure case-insensitive search
    if room:
        # Map URL generation with latitude and longitude
        if 'latitude' in room and 'longitude' in room:
            map_url = f"https://www.google.com/maps/search/?api=1&query={room['latitude']},{room['longitude']}"
            return (f"Room {room['room']} is located in {room['building']}. Directions: {room['directions']}. "
                    f"Here's a map: <a href='{map_url}' target='_blank'>View on Google Maps</a>. "
                    f"Image: <img src='{request.url_root.rstrip('/')}/{room['image']}' alt='{room['room']}' width='200'>")
        else:
            return (f"Room {room['room']} is located in {room['building']}. Directions: {room['directions']}. "
                    f"Image: <img src='{request.url_root.rstrip('/')}/{room['image']}' alt='{room['room']}' width='200'>")
    else:
        return "Sorry, I couldn't find that room. Please check the room name or number."

# Chatbot API route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    question = data.get("message")

    if not question:
        return jsonify({"response": "Please provide a valid input."}), 400

    answer = generate_response(question)
    return jsonify({"response": answer})

# Endpoint to add a new room with an image
@app.route('/add_room', methods=['POST'])
def add_room():
    room_name = request.form.get('room_name')
    building = request.form.get('building')
    directions = request.form.get('directions')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    image = request.files.get('image')

    if not room_name or not building or not directions or not image:
        return jsonify({"error": "All fields (room name, building, directions, image) are required."}), 400

    if not allowed_file(image.filename):
        return jsonify({"error": "Invalid image file format. Allowed formats: png, jpg, jpeg, gif."}), 400

    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    # Debugging log
    print(f"Image saved to: {image_path}")

    # Store room details in the 'rooms' dictionary
    rooms[room_name.lower()] = {
        "room": room_name,
        "building": building,
        "directions": directions,
        "latitude": latitude,
        "longitude": longitude,
        "image": f"{UPLOAD_FOLDER}/{filename}"
    }

    return jsonify({"message": f"Room '{room_name}' added successfully."})

# Serve the home page
@app.route('/')
def home():
    return render_template('index.html')

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
