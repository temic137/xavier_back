let isProcessing = false;

function toggleChat() {
    const container = document.getElementById('chatbot-container');
    if (container.style.display === 'none') {
        container.innerHTML = `
            <div id="chatbot-header">
                <span>Chat with ${window.chatbotConfig.name}</span>
                <span id="chatbot-close" onclick="toggleChat()">×</span>
            </div>
            <div id="chatbot-messages"></div>
            <div id="typing-indicator">Typing...</div>
            <div id="chatbot-input">
                <input type="text" id="chatbot-text" placeholder="Type your message..." aria-label="Chat message">
                <button id="send-button" onclick="sendMessage()">Send</button>
            </div>
        `;
        container.style.display = 'block';
        document.getElementById('chatbot-text').focus();
    } else {
        container.style.display = 'none';
    }
}

function sendMessage() {
    const messageInput = document.getElementById('chatbot-text');
    const message = messageInput.value.trim();
    
    if (message === '' || isProcessing) return;
    
    appendMessage(message, true);
    messageInput.value = '';
    
    showTypingIndicator();
    isProcessing = true;

    fetch(window.chatbotConfig.apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: message })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        appendMessage(data.answer, false);
    })
    .catch(error => {
        console.error('Error:', error);
        hideTypingIndicator();
        appendMessage('Sorry, I encountered an error.', false);
    })
    .finally(() => {
        isProcessing = false;
    });
}

function appendMessage(message, isUser) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.textContent = isUser ? `You: ${message}` : `Bot: ${message}`;
    messageDiv.className = isUser ? 'user-message' : 'bot-message';
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'block';
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('chatbot-icon').innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
    
    document.getElementById('chatbot-text')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});