(function() {
    // Configuration and Setup
    const script = document.currentScript;
    const config = {
        chatbotId: script.getAttribute('data-chatbot-id'),
        name: script.getAttribute('data-name') || 'Support Agent',
        askUrl: script.getAttribute('data-ask-url'),
        feedbackUrl: script.getAttribute('data-feedback-url'),
        sentimentUrl: script.getAttribute('data-sentiment-url'),
        ticketUrl: script.getAttribute('data-ticket-url'),
        avatar: script.getAttribute('data-avatar') || './assets/agent.png',
        themeColor: script.getAttribute('data-theme-color') || '#0066CC'
    };

    // Constants
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000;
    const INITIAL_POLL_DELAY = 1000;
    const MAX_POLL_DELAY = 10000;

    // Styles
    const styles = `
        .chatbot-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            z-index: 999999;
            width: 360px;
            line-height: normal;
        }

        .chatbot-toggle {
            background: ${config.themeColor};
            color: white;
            border: none;
            padding: 16px;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: auto;
        }

        .chatbot-toggle:hover {
            background: ${adjustColor(config.themeColor, -20)};
            transform: scale(1.05);
        }

        .chatbot-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid white;
            object-fit: cover;
        }

        .chatbot-content {
            display: none;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-bottom: 16px;
            overflow: hidden;
            height: 480px;
            flex-direction: column;
            position: relative;
        }

        .chatbot-content.chatbot-visible {
            display: flex;
        }

        .chatbot-header {
            padding: 20px;
            background: ${config.themeColor};
            color: #FFFFFF;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            position: relative;
        }

        .chatbot-header-info {
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 1;
        }

        .chatbot-status-dot {
            width: 8px;
            height: 8px;
            background: #22C55E;
            border-radius: 50%;
            margin-right: 4px;
            display: inline-block;
        }

        .chatbot-messages {
            flex-grow: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }

        .chatbot-message {
            margin-bottom: 12px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 85%;
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
        }

        .chatbot-message.user {
            background: ${config.themeColor};
            color: white;
            margin-left: auto;
        }

        .chatbot-message.bot {
            background: white;
            color: #1a1a1a;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .chatbot-message.agent {
            background: #e3f2fd;
            color: #1a237e;
            border-bottom-left-radius: 4px;
        }

        .chatbot-message.system {
            background: #f5f5f5;
            color: #666;
            font-style: italic;
            text-align: center;
            margin: 10px auto;
            width: 80%;
        }

        .chatbot-input-container {
            padding: 16px;
            background: white;
            border-top: 1px solid #eee;
        }

        .chatbot-input-wrapper {
            display: flex;
            align-items: center;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 8px 16px;
            gap: 8px;
        }

        .chatbot-input {
            flex-grow: 1;
            border: none;
            background: transparent;
            padding: 8px 0;
            font-size: 14px;
            color: #1a1a1a;
        }

        .chatbot-escalate-button {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 14px;
            transition: all 0.2s ease;
            color: white;
            cursor: pointer;
        }

        .chatbot-escalate-button:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .chatbot-typing {
            padding: 12px 16px;
            background: #F5F5F5;
            border-radius: 12px;
            display: inline-block;
            margin-bottom: 12px;
        }

        .chatbot-typing-dots {
            display: flex;
            gap: 4px;
            padding: 0 4px;
        }

        .chatbot-typing-dot {
            width: 8px;
            height: 8px;
            background: ${config.themeColor};
            border-radius: 50%;
            animation: typing 1.4s infinite;
            opacity: 0.2;
        }

        @keyframes typing {
            0%, 100% { opacity: 0.2; transform: translateY(0); }
            50% { opacity: 1; transform: translateY(-2px); }
        }

        .connection-loader {
            border: 2px solid #f3f3f3;
            border-top: 2px solid ${config.themeColor};
            border-radius: 50%;
            width: 16px;
            height: 16px;
            animation: spin 1s linear infinite;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }

        .chatbot-retry-options {
            text-align: center;
            margin-top: 1rem;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .retry-button, .ticket-button {
            background: ${config.themeColor};
            color: white;
            border: none;
            padding: 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: opacity 0.2s;
        }

        .retry-button:hover, .ticket-button:hover {
            opacity: 0.9;
        }

        .retry-divider {
            color: #666;
            margin: 4px 0;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .chatbot-status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }

        .status-dot.connecting {
            background: #FFD700;
            animation: pulse 1.5s infinite;
        }

        .status-dot.connected {
            background: #22C55E;
        }

        .status-dot.error {
            background: #EF4444;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    `;

    function adjustColor(color, amount) {
        const hex = color.replace('#', '');
        const r = Math.max(0, Math.min(255, parseInt(hex.substr(0, 2), 16) + amount));
        const g = Math.max(0, Math.min(255, parseInt(hex.substr(2, 2), 16) + amount));
        const b = Math.max(0, Math.min(255, parseInt(hex.substr(4, 2), 16) + amount));
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    // Inject styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // HTML Structure
    const widget = document.createElement('div');
    widget.innerHTML = `
        <div id="chatbot-widget" class="chatbot-container">
            <button id="chatbot-toggle" class="chatbot-toggle">
                <svg viewBox="0 0 60 60" fill="white" width="24" height="24">
                    <path d="M59.949,58.684L55.104,44.15C57.654,39.702,59,34.647,59,29.5C59,13.233,45.767,0,29.5,0S0,13.233,0,29.5S13.233,59,29.5,59c4.64,0,9.257-1.108,13.378-3.208l15.867,4.176C58.83,59.989,58.915,60,59,60c0.272,0,0.538-0.112,0.729-0.316C59.98,59.416,60.065,59.032,59.949,58.684z M16,21.015h14c0.552,0,1,0.448,1,1s-0.448,1-1,1H16c-0.552,0-1-0.448-1-1S15.448,21.015,16,21.015z M43,39.015H16c-0.552,0-1-0.448-1-1s0.448-1,1-1h27c0.552,0,1,0.448,1,1S43.552,39.015,43,39.015z M43,31.015H16c-0.552,0-1-0.448-1-1s0.448-1,1-1h27c0.552,0,1,0.448,1,1S43.552,31.015,43,31.015z"/>
                </svg>
            </button>
            
            <div id="chatbot-content" class="chatbot-content">
                <div class="chatbot-header">
                    <div class="chatbot-header-info">
                        <img src="${config.avatar}" class="chatbot-avatar" alt="${config.name}">
                        <div class="chatbot-header-text">
                            <div style="font-weight: 600">${config.name}</div>
                            <div class="chatbot-status-indicator">
                                <div class="status-dot connecting"></div>
                                <span>Connecting...</span>
                            </div>
                        </div>
                    </div>
                    
                    <button class="chatbot-escalate-button" onclick="window.chatbotWidget.escalateChat()">
                        Talk to Agent
                    </button>
                    
                    <button class="chatbot-close-chat" onclick="window.chatbotWidget.toggle()">×</button>
                </div>
                
                <div id="chatbot-messages" class="chatbot-messages">
                    <div class="chatbot-message bot">
                        Hi there! 👋 How can I help you today?
                    </div>
                </div>
                
                <div class="chatbot-input-container">
                    <div class="chatbot-input-wrapper">
                        <input type="text" 
                               id="chatbot-input" 
                               class="chatbot-input"
                               placeholder="Type your message..."
                               autocomplete="off"
                               onkeypress="if(event.key === 'Enter') window.chatbotWidget.send()">
                        <button id="chatbot-send" onclick="window.chatbotWidget.send()" class="chatbot-send">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${config.themeColor}">
                                <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(widget);

    // Core Functionality
    window.chatbotWidget = {
        isOpen: false,
        isEscalated: false,
        escalationId: null,
        retryCount: 0,
        pollTimeout: INITIAL_POLL_DELAY,
        userId: 'user_' + Math.random().toString(36).substr(2, 9),

        initialize() {
            this.toggle();
            this.setupEventListeners();
            this.updateConnectionStatus('connecting');
        },

        toggle() {
            const content = document.getElementById('chatbot-content');
            const toggle = document.getElementById('chatbot-toggle');
            content.classList.toggle('chatbot-visible');
            toggle.style.display = content.classList.contains('chatbot-visible') ? 'none' : 'flex';
        },

        setupEventListeners() {
            const input = document.getElementById('chatbot-input');
            input.addEventListener('input', () => {
                document.getElementById('chatbot-send').disabled = !input.value.trim();
            });
        },

        // Escalation Management
        async escalateChat() {
            if (this.isEscalated) return;
            
            this.showSystemMessage('Connecting you to a live agent...');
            this.updateConnectionStatus('connecting');
            const escalateButton = document.querySelector('.chatbot-escalate-button');
            escalateButton.disabled = true;
            escalateButton.innerHTML = '<div class="connection-loader"></div> Connecting...';

            try {
                const response = await fetch(`/escalate/${config.chatbotId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'User-ID': this.userId
                    }
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.message || 'Connection failed');
                }

                const data = await response.json();
                this.escalationId = data.escalation_id;
                this.startEscalationPolling();
                this.startMessagePolling();
                this.retryCount = 0;
                this.pollTimeout = INITIAL_POLL_DELAY;

            } catch (error) {
                this.handleConnectionError(error, escalateButton);
            }
        },

        startEscalationPolling() {
            const poll = async () => {
                try {
                    const response = await fetch(`/escalation/${this.escalationId}/poll`);
                    
                    if (!response.ok) {
                        throw new Error('Polling failed');
                    }

                    const data = await response.json();
                    
                    if (data.status === 'connected') {
                        this.handleAgentConnected();
                    } else {
                        this.pollTimeout = Math.min(this.pollTimeout * 2, MAX_POLL_DELAY);
                        setTimeout(poll, this.pollTimeout);
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                    this.pollTimeout = Math.min(this.pollTimeout * 2, MAX_POLL_DELAY);
                    setTimeout(poll, this.pollTimeout);
                }
            };
            
            poll();
        },

        startMessagePolling() {
            const poll = async () => {
                if (!this.isEscalated || !this.escalationId) return;
                
                try {
                    const response = await fetch(`/escalation/${this.escalationId}/messages`);
                    const data = await response.json();
                    
                    if (data.messages?.length > 0) {
                        data.messages.forEach(msg => this.displayAgentMessage(msg));
                    }
                    setTimeout(poll, 1000);
                } catch (error) {
                    setTimeout(poll, 1000);
                }
            };
            poll();
        },

        handleAgentConnected() {
            this.isEscalated = true;
            this.updateConnectionStatus('connected');
            this.showSystemMessage('Connected to live agent!');
            
            const escalateButton = document.querySelector('.chatbot-escalate-button');
            escalateButton.textContent = 'Connected ✓';
            escalateButton.disabled = true;
            
            document.getElementById('chatbot-input').placeholder = 'Type to chat with agent...';
        },

        handleConnectionError(error, button) {
            this.retryCount++;
            this.updateConnectionStatus('error');
            
            if (this.retryCount < MAX_RETRIES) {
                this.showSystemMessage(
                    `Connection attempt ${this.retryCount}/${MAX_RETRIES}. Retrying...`
                );
                setTimeout(() => this.escalateChat(), RETRY_DELAY);
            } else {
                this.showSystemMessage(
                    'Failed to connect. Please try again later or create a support ticket.',
                    true
                );
                button.disabled = false;
                button.textContent = 'Talk to Agent';
                this.showRetryOptions();
            }
        },

        showRetryOptions() {
            const messages = document.getElementById('chatbot-messages');
            const retryDiv = document.createElement('div');
            retryDiv.className = 'chatbot-retry-options';
            retryDiv.innerHTML = `
                <button class="retry-button" onclick="window.chatbotWidget.escalateChat()">
                    Retry Connection
                </button>
                <span class="retry-divider">or</span>
                <button class="ticket-button" onclick="window.chatbotWidget.openTicketForm()">
                    Create Support Ticket
                </button>
            `;
            messages.appendChild(retryDiv);
        },

        updateConnectionStatus(status) {
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.chatbot-status-indicator span');
            
            statusDot.className = 'status-dot ' + status;
            
            switch(status) {
                case 'connecting':
                    statusText.textContent = 'Connecting...';
                    break;
                case 'connected':
                    statusText.textContent = 'Connected';
                    break;
                case 'error':
                    statusText.textContent = 'Connection Failed';
                    break;
            }
        },

        // Message Handling
        async send() {
            const input = document.getElementById('chatbot-input');
            const message = input.value.trim();
            if (!message) return;

            this.displayMessage(message, 'user');
            input.value = '';
            document.getElementById('chatbot-send').disabled = true;

            if (this.isEscalated) {
                this.sendEscalationMessage(message);
            } else {
                this.sendToBot(message);
            }
        },

        async sendToBot(message) {
            this.showTyping();
            
            try {
                const response = await fetch(config.askUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'User-ID': this.userId
                    },
                    body: JSON.stringify({ question: message })
                });
                
                const data = await response.json();
                this.displayMessage(data.answer, 'bot');
            } catch (error) {
                this.displayMessage('Sorry, something went wrong. Please try again.', 'error');
            } finally {
                this.hideTyping();
            }
        },

        async sendEscalationMessage(message) {
            try {
                await fetch(`/escalation/${this.escalationId}/message`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'User-ID': this.userId
                    },
                    body: JSON.stringify({
                        message: message,
                        sender: 'user'
                    })
                });
            } catch (error) {
                this.showSystemMessage('Failed to send message. Please try again.', true);
            }
        },

        // UI Helpers
        displayMessage(text, type) {
            const messages = document.getElementById('chatbot-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chatbot-message ${type}`;
            messageDiv.textContent = text;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        },

        showSystemMessage(text, isError = false) {
            const messages = document.getElementById('chatbot-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chatbot-message system ${isError ? 'error' : ''}`;
            messageDiv.textContent = text;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        },

        showTyping() {
            const messages = document.getElementById('chatbot-messages');
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.className = 'chatbot-typing';
            typingDiv.innerHTML = `
                <div class="chatbot-typing-dots">
                    <div class="chatbot-typing-dot"></div>
                    <div class="chatbot-typing-dot"></div>
                    <div class="chatbot-typing-dot"></div>
                </div>
            `;
            messages.appendChild(typingDiv);
            messages.scrollTop = messages.scrollHeight;
        },

        hideTyping() {
            const typing = document.getElementById('typing-indicator');
            if (typing) typing.remove();
        }
    };

    // Initialize
    window.chatbotWidget.initialize();
})();