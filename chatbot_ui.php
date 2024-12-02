<?php
session_start();
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot UI </title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        body { display: flex; min-height: 100vh; }
        .sidebar { width: 250px; background-color: #343a40; color: #fff; padding: 20px; border-right: 1px solid #ddd; overflow-y: auto; }
        .content { flex-grow: 1; display: flex; flex-direction: column; padding: 20px; }
        .chat-output { height: 400px; overflow-y: auto; }
        .type-bar { position: fixed; bottom: 0; left: 0; right: 0; padding: 10px; background-color: #f8f9fa; border-top: 1px solid #ddd; }
        .sidebar a { color: #ffffff; text-decoration: none; margin-bottom: 10px; display: block; padding: 10px; border-radius: 5px; }
        .sidebar a:hover { background-color: #495057; }

        .typing-indicator {
            font-style: italic;
            color: #aaa;
        }

        @media (max-width: 768px) {
            .sidebar { width: 100%; position: relative; }
            .type-bar { left: 0; right: 0; }
        }

        @media (min-width: 769px) {
            .type-bar { left: 250px; width: calc(100% - 250px); }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <a href="#home"><i class="fas fa-home"></i> Home</a>
        <a href="#manage-settings"><i class="fas fa-cog"></i> Manage System Settings</a>
        <a href="#manage-responses"><i class="fas fa-comments"></i> Manage Responses</a>
        <a href="#unanswered-queries"><i class="fas fa-question-circle"></i> Manage Unanswered Queries</a>
        <hr>
        <a href="logout.php"><i class="fas fa-sign-out-alt"></i> Logout</a>
    </div>
    <div class="content">
        <h2 class="text-center">NMSCST STUDENT GUIDE <img src="nmsc.png" style="width: 70px; height: auto;"></h2> 
        <div class="card mt-4">
            <div class="card-body">
                <div id="chat-output" class="chat-output border rounded p-3 mb-3">
                    <p>Chatbot: Hello! How can I assist you today?</p>
                </div>
            </div>
        </div>
        <div class="type-bar">
            <form id="chat-form" class="d-flex">
                <input type="text" id="user-input" class="form-control me-2" placeholder="Type your message..." required>
                <button type="button" class="btn btn-secondary" onclick="startSpeechRecognition()"><i class="fas fa-microphone"></i></button>
                <button type="submit" class="btn btn-primary ms-2"><i class="fas fa-paper-plane"></i></button>
            </form>
            <div id="typing-indicator" class="typing-indicator d-none">Chatbot is typing...</div>
        </div>
    </div>

    <script>
        const chatForm = document.getElementById('chat-form');
        const userInput = document.getElementById('user-input');
        const chatOutput = document.getElementById('chat-output');
        const typingIndicator = document.getElementById('typing-indicator');

        const flaskApiUrl = 'http://127.0.0.1:5000/chatbot';

        chatForm.onsubmit = async function(event) {
            event.preventDefault();
            const message = userInput.value;
            addChatMessage('You', message);
            userInput.value = '';
            typingIndicator.classList.remove('d-none');

            try {
                const response = await fetch(flaskApiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                const data = await response.json();
                const botMessage = data.response || "I'm sorry, I couldn't understand that.";
                addChatMessage('Bot', botMessage);
            } catch (error) {
                console.error("Error:", error);
                addChatMessage('Bot', "Error: Could not connect to the server.");
            } finally {
                typingIndicator.classList.add('d-none');
            }
        };

        function addChatMessage(sender, message) {
            chatOutput.innerHTML += `<p><strong>${sender}:</strong> ${message}</p>`;
            chatOutput.scrollTop = chatOutput.scrollHeight;
        }

        function startSpeechRecognition() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.start();

            recognition.onresult = function(event) {
                userInput.value = event.results[0][0].transcript;
            };

            recognition.onerror = function() {
                alert('Sorry, I couldn\'t understand that. Please try again.');
            };
        }
    </script>
</body>
</html>
