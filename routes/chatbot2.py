
# @chatbot_bp.route('/get_chatbot_script/<chatbot_id>')
# @handle_errors
# def get_chatbot_script(chatbot_id):
#     chatbot = Chatbot.query.get(chatbot_id)
#     if not chatbot:
#         return jsonify({"error": "Chatbot not found"}), 404
    
#     integration_code = f"""

# <div id="chatbot-icon" onclick="toggleChat()" style="position: fixed; bottom: 20px; right: 20px; width: 50px; height: 50px; background-color: #4a5568; border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; z-index: 1000;" aria-label="Toggle chat">
#     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
#         <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
#     </svg>
# </div>

# <div id="chatbot-container" style="position: fixed; bottom: 20px; right: 20px; width: 300px; height: 400px; border: 1px solid #ccc; border-radius: 10px; overflow: hidden;">
#     <div id="chatbot-header" style="background-color: #4a5568; color: white; padding: 10px; font-weight: bold;">
#         Chat with {chatbot.name}
#     </div>
#     <div id="chatbot-messages" style="height: 300px; overflow-y: auto; padding: 10px;"></div>
#         <div id="chatbot-input" style="display: flex; padding: 10px;">
#             <input type="text" id="chatbot-text" style="flex-grow: 1; padding: 5px; border: 1px solid #ccc; border-radius: 3px;" placeholder="Type your message..." aria-label="Chat message">
#             <button id="send-button" onclick="sendMessage()" style="background-color: #4a5568; color: white; border: none; padding: 5px 10px; margin-left: 5px; cursor: pointer; border-radius: 3px;">Send</button>
#     </div>
# </div>

# <script>

# function toggleChat() {{
#         const chatContainer = document.getElementById('chatbot-container');
#         chatContainer.style.display = chatContainer.style.display === 'none' ? 'block' : 'none';
#     }}
    
# function sendMessage() {{
#     var message = document.getElementById('chatbot-text').value;
#     if (message.trim() === '') return;

#     appendMessage('You: ' + message);
#     document.getElementById('chatbot-text').value = '';

#     fetch('{request.host_url}chatbot/{chatbot_id}/ask', {{
#         method: 'POST',
#         headers: {{
#             'Content-Type': 'application/json',
#         }},
#         body: JSON.stringify({{ question: message }})
#     }})
#     .then(response => response.json())
#     .then(data => {{
#         appendMessage('Bot: ' + data.answer);
#     }})
#     .catch((error) => {{
#         console.error('Error:', error);
#         appendMessage('Bot: Sorry, I encountered an error.');
#     }});
# }}

# function appendMessage(message) {{
#     var messageDiv = document.createElement('div');
#     messageDiv.textContent = message;
#     messageDiv.style.marginBottom = '10px';
#     messageDiv.style.padding = '5px';
#     messageDiv.style.borderRadius = '5px';
#     messageDiv.style.backgroundColor= '#e6f3ff';
#     document.getElementById('chatbot-messages').appendChild(messageDiv);
#     document.getElementById('chatbot-messages').scrollTop = document.getElementById('chatbot-messages').scrollHeight;
# }}
# </script>
#  """

#     return jsonify({ 'integration_code' : integration_code })





# """
#     <div id="chatbot-container" style="position: fixed; bottom: 20px; right: 20px; width: 300px; height: 400px; border: 1px solid #ccc; border-radius: 10px; overflow: hidden;">
#         <div id="chatbot-header" style="background-color: #4a5568; color: white; padding: 10px; font-weight: bold;">
#             Chat with {chatbot.name}
#         </div>
#         <div id="chatbot-messages" style="height: 300px; overflow-y: auto; padding: 10px; background-color:white;"></div>
#         <div id="chatbot-input" style="display: flex; padding: 10px;">
#             <input type="text" id="chatbot-text" style="flex-grow: 1; padding: 5px;" placeholder="Type your message...">
#             <button onclick="sendMessage()" style="background-color: #4a5568; color: white; border: none; padding: 5px 10px; margin-left: 5px;">Send</button>
#         </div>
#     </div>

#     <script>
#     function sendMessage() {{
#         var message = document.getElementById('chatbot-text').value;
#         if (message.trim() === '') return;

#         appendMessage('You: ' + message);
#         document.getElementById('chatbot-text').value = '';

#         fetch('{request.host_url}chatbot/{chatbot_id}/ask', {{
#             method: 'POST',
#             headers: {{
#                 'Content-Type': 'application/json',
#             }},
#             body: JSON.stringify({{ question: message }})
#         }})
#         .then(response => response.json())
#         .then(data => {{
#             appendMessage('Bot: ' + data.answer);
#         }})
#         .catch((error) => {{
#             console.error('Error:', error);
#             appendMessage('Bot: Sorry, I encountered an error.');
#         }});
#     }}

#     function appendMessage(message) {{
#         var messageDiv = document.createElement('div');
#         messageDiv.textContent = message;
#         document.getElementById('chatbot-messages').appendChild(messageDiv);
#         document.getElementById('chatbot-messages').scrollTop = document.getElementById('chatbot-messages').scrollHeight;
#     }}
#     </script>
#      """
    