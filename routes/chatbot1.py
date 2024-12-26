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
    

























# <div id="chatbot-icon" onclick="toggleChat()" style="
#     position: fixed;
#     bottom: 20px;
#     right: 20px;
#     width: 50px;
#     height: 50px;
#     background-color: #4a5568;
#     border-radius: 50%;
#     display: flex;
#     justify-content: center;
#     align-items: center;
#     cursor: pointer;
#     z-index: 1000;
#     box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#     transition: transform 0.3s ease;
# " aria-label="Toggle chat" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
#     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
#         <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
#     </svg>
# </div>

# <div id="chatbot-container" style="
#     position: fixed;
#     bottom: 20px;
#     right: 20px;
#     width: 300px;
#     max-height: 500px;
#     border: 1px solid #ccc;
#     border-radius: 10px;
#     overflow: hidden;
#     display: none;
#     box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
#     font-family: Arial, sans-serif;
# ">
#     <div id="chatbot-header" style="
#         background-color: #4a5568;
#         color: white;
#         padding: 10px;
#         font-weight: bold;
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#     ">
#         <span>Chat with {chatbot.name}</span>
#         <div> feedback 
#             <span id="feedback-button" onclick="openFeedbackModal()" style="
#                 color: white;
#                 cursor: pointer;
#                 margin-right: 10px;
#             " aria-label="Give Feedback">
#                 &#128172;
#             </span>
#             <span id="chatbot-close" onclick="toggleChat()" style="
#                 color: white;
#                 cursor: pointer;
#                 font-size: 20px;
#             ">&times;</span>
#         </div>
#     </div>
#     <div id="chatbot-messages" style="
#         height: 350px;
#         overflow-y: auto;
#         padding: 10px;
#         background-color: #f9f9f9;
#         display: flex;
#         flex-direction: column;
#     "></div>
#     <div id="typing-indicator" style="
#         display: none;
#         padding: 10px;
#         text-align: center;
#         font-style: italic;
#         color: #666;
#     ">Typing...</div>
#     <div id="chatbot-input" style="
#         display: flex;
#         padding: 10px;
#         background-color: white;
#         border-top: 1px solid #eee;
#     ">
#         <input type="text" id="chatbot-text" placeholder="Type your message..." aria-label="Chat message" style="
#             flex-grow: 1;
#             padding: 8px;
#             border: 1px solid #ccc;
#             border-radius: 3px;
#             outline: none;
#         ">
#         <button id="send-button" onclick="sendMessage()" style="
#             background-color: #4a5568;
#             color: white;
#             border: none;
#             padding: 8px 15px;
#             margin-left: 5px;
#             cursor: pointer;
#             border-radius: 3px;
#             transition: background-color 0.3s ease;
#         ">Send</button>
#     </div>
# </div>

# <!-- Feedback Modal -->
# <div id="feedback-modal" style="
#     display: none;
#     position: fixed;
#     z-index: 1100;
#     left: 0;
#     top: 0;
#     width: 100%;
#     height: 100%;
#     overflow: auto;
#     background-color: rgba(0,0,0,0.4);
#     justify-content: center;
#     align-items: center;
# ">
#     <div style="
#         background-color: white;
#         padding: 20px;
#         border-radius: 10px;
#         width: 300px;
#         max-width: 90%;
#         box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#     ">
#         <div style="
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#             margin-bottom: 15px;
#         ">
#             <h2 style="margin: 0; font-size: 18px;">Feedback</h2>
#             <span onclick="closeFeedbackModal()" style="
#                 color: #aaa;
#                 font-size: 28px;
#                 font-weight: bold;
#                 cursor: pointer;
#             ">&times;</span>
#         </div>
#         <textarea id="feedback-text" placeholder="Share your feedback..." style="
#             width: 100%;
#             height: 100px;
#             margin-bottom: 15px;
#             padding: 10px;
#             border: 1px solid #ccc;
#             border-radius: 5px;
#             resize: none;
#         "></textarea>
#         <div style="display: flex; justify-content: space-between;">
#             <button onclick="submitFeedback()" style="
#                 background-color: #4a5568;
#                 color: white;
#                 border: none;
#                 padding: 10px 15px;
#                 border-radius: 5px;
#                 cursor: pointer;
#             ">Submit Feedback</button>
#             <button onclick="closeFeedbackModal()" style="
#                 background-color: #f0f0f0;
#                 color: #333;
#                 border: none;
#                 padding: 10px 15px;
#                 border-radius: 5px;
#                 cursor: pointer;
#             ">Cancel</button>
#         </div>
#     </div>
# </div>

# <script>
# let isProcessing = false;
# let userId = generateUserId(); // Generate a unique user ID

# function generateUserId() {{
#     return 'user_' + Math.random().toString(36).substr(2, 9);
# }}

# function toggleChat() {{
#     const chatContainer = document.getElementById('chatbot-container');
#     const isHidden = chatContainer.style.display === 'none';
#     chatContainer.style.display = isHidden ? 'block' : 'none';
    
#     if (isHidden) {{
#         document.getElementById('chatbot-text').focus();
#     }}
# }}

# function sendMessage() {{
#     const messageInput = document.getElementById('chatbot-text');
#     const message = messageInput.value.trim();
    
#     if (message === '' || isProcessing) return;
    
#     appendMessage(message, true);
#     messageInput.value = '';
    
#     showTypingIndicator();
#     isProcessing = true;

#     fetch('{request.host_url}chatbot/{chatbot_id}/ask', {{
#         method: 'POST',
#         headers: {{
#             'Content-Type': 'application/json',
#         }},
#         body: JSON.stringify({{ question: message }})
#     }})
#     .then(response => {{
#         if (!response.ok) {{
#             throw new Error('Network response was not ok');
#         }}
#         return response.json();
#     }})
#     .then(data => {{
#         hideTypingIndicator();
#         appendMessage(data.answer, false);
#     }})
#     .catch((error) => {{
#         console.error('Error:', error);
#         hideTypingIndicator();
#         appendMessage('Sorry, I encountered an error.', false);
#     }})
#     .finally(() => {{
#         isProcessing = false;
#     }});
# }}

# function appendMessage(message, isUser) {{
#     const messagesContainer = document.getElementById('chatbot-messages');
#     const messageDiv = document.createElement('div');
    
#     messageDiv.textContent = isUser ? `You: ${{message}}` : `Bot: ${{message}}`;
#     messageDiv.style.cssText = `
#         max-width: 80%;
#         margin: 10px 0;
#         padding: 8px 12px;
#         border-radius: 12px;
#         clear: both;
#         align-self: ${{isUser ? 'flex-end' : 'flex-start'}};
#         margin-left: ${{isUser ? 'auto' : '0'}};
#         background-color: ${{isUser ? '#4a5568' : '#e6f3ff'}};
#         color: ${{isUser ? 'white' : '#333'}};
#     `;
    
#     messagesContainer.appendChild(messageDiv);
#     messagesContainer.scrollTop = messagesContainer.scrollHeight;
# }}

# function showTypingIndicator() {{
#     document.getElementById('typing-indicator').style.display = 'block';
# }}

# function hideTypingIndicator() {{
#     document.getElementById('typing-indicator').style.display = 'none';
# }}

# function openFeedbackModal() {{
#     document.getElementById('feedback-modal').style.display = 'flex';
# }}

# function closeFeedbackModal() {{
#     document.getElementById('feedback-modal').style.display = 'none';
#     document.getElementById('feedback-text').value = '';
# }}

# function submitFeedback() {{
#     const feedbackText = document.getElementById('feedback-text').value.trim();
    
#     if (feedbackText === '') {{
#         alert('Please enter your feedback.');
#         return;
#     }}

#     fetch('{request.host_url}chatbot/{chatbot_id}/feedback', {{
#         method: 'POST',
#         headers: {{
#             'Content-Type': 'application/json',
#             'User-ID': userId
#         }},
#         body: JSON.stringify({{ feedback: feedbackText }})
#     }})
#     .then(response => {{
#         if (!response.ok) {{
#             throw new Error('Network response was not ok');
#         }}
#         return response.json();
#     }})
#     .then(data => {{
#         alert('Feedback submitted successfully!');
#         closeFeedbackModal();
#     }})
#     .catch((error) => {{
#         console.error('Error:', error);
#         alert('Failed to submit feedback. Please try again.');
#     }});
# }}

# // Allow sending message with Enter key
# document.getElementById('chatbot-text').addEventListener('keypress', function(e) {{
#     if (e.key === 'Enter') {{
#         sendMessage();
#     }}
# }});
# </script>