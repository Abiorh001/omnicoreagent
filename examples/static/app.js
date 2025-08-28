// Enhanced OmniAgent Web Interface JavaScript
class OmniAgentInterface {
    constructor() {
        this.currentSessionId = null;
        this.isStreaming = false;
        this.websocket = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTabs();
        this.loadTools();
        this.loadBackgroundAgents();
        this.loadEvents();
        this.connectWebSocket();
    }

    setupEventListeners() {
        // Chat functionality
        const chatForm = document.getElementById('chat-form');
        const chatInput = document.getElementById('chat-input');
        
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Background agent form
        const bgAgentForm = document.getElementById('bg-agent-form');
        if (bgAgentForm) {
            bgAgentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createBackgroundAgent();
            });
        }

        // Task update form
        const taskUpdateForm = document.getElementById('task-update-form');
        if (taskUpdateForm) {
            taskUpdateForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateTask();
            });
        }
    }

    setupTabs() {
        const tabs = document.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll('.tab-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.getAttribute('data-target');
                
                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(tc => tc.classList.remove('active'));
                
                // Add active class to clicked tab and target content
                tab.classList.add('active');
                document.getElementById(target).classList.add('active');
            });
        });

        // Set first tab as active by default
        if (tabs.length > 0) {
            tabs[0].click();
        }
    }

    async sendMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput.value.trim();
        
        if (!message || this.isStreaming) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        chatInput.value = '';

        // Show streaming indicator
        this.isStreaming = true;
        const streamingId = this.addMessage('Thinking...', 'agent', 'streaming');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponse = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.type === 'chunk') {
                                fullResponse += data.content;
                                this.updateMessage(streamingId, fullResponse);
                            } else if (data.type === 'complete') {
                                this.isStreaming = false;
                                this.currentSessionId = data.session_id;
                                this.updateMessage(streamingId, fullResponse);
                                this.loadEvents(); // Refresh events
                            } else if (data.type === 'error') {
                                this.isStreaming = false;
                                this.updateMessage(streamingId, `Error: ${data.content}`, 'error');
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.isStreaming = false;
            this.updateMessage(streamingId, `Error: ${error.message}`, 'error');
        }
    }

    addMessage(content, type, className = '') {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return null;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type} ${className}`;
        messageDiv.textContent = content;
        
        if (className === 'streaming') {
            messageDiv.id = `streaming-${Date.now()}`;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv.id;
    }

    updateMessage(messageId, content, className = '') {
        const messageDiv = document.getElementById(messageId);
        if (messageDiv) {
            messageDiv.textContent = content;
            if (className) {
                messageDiv.className = `message agent ${className}`;
            }
        }
    }

    async createBackgroundAgent() {
        const agentId = document.getElementById('agent-id').value;
        const query = document.getElementById('agent-query').value;
        const schedule = document.getElementById('agent-schedule').value;

        if (!agentId || !query) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        try {
            const response = await fetch('/api/background/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_id: agentId,
                    query: query,
                    schedule: schedule || null
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification('Background agent created successfully!', 'success');
                this.loadBackgroundAgents();
                document.getElementById('bg-agent-form').reset();
            } else {
                const error = await response.json();
                this.showNotification(`Error: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error creating background agent:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async loadBackgroundAgents() {
        try {
            const response = await fetch('/api/background/list');
            if (response.ok) {
                const result = await response.json();
                this.displayBackgroundAgents(result.agents || []);
            }
        } catch (error) {
            console.error('Error loading background agents:', error);
        }
    }

    displayBackgroundAgents(agents) {
        const container = document.getElementById('background-agents-list');
        if (!container) return;

        if (agents.length === 0) {
            container.innerHTML = '<p>No background agents running</p>';
            return;
        }

        const html = agents.map(agent => `
            <div class="card">
                <h4>${agent.agent_id}</h4>
                <p><strong>Query:</strong> ${agent.query}</p>
                <p><strong>Status:</strong> 
                    <span class="status-indicator status-${agent.status || 'pending'}"></span>
                    ${agent.status || 'pending'}
                </p>
                <p><strong>Created:</strong> ${new Date(agent.created_at).toLocaleString()}</p>
                <div class="btn-group">
                    <button class="btn btn-primary" onclick="omniInterface.startBackgroundAgent('${agent.agent_id}')">
                        Start
                    </button>
                    <button class="btn btn-danger" onclick="omniInterface.stopBackgroundAgent('${agent.agent_id}')">
                        Stop
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async startBackgroundAgent(agentId) {
        try {
            const response = await fetch('/api/background/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_id: agentId,
                    query: ''
                })
            });

            if (response.ok) {
                this.showNotification('Background agent started!', 'success');
                this.loadBackgroundAgents();
            } else {
                const error = await response.json();
                this.showNotification(`Error: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error starting background agent:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async stopBackgroundAgent(agentId) {
        try {
            const response = await fetch('/api/background/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_id: agentId,
                    query: ''
                })
            });

            if (response.ok) {
                this.showNotification('Background agent stopped!', 'success');
                this.loadBackgroundAgents();
            } else {
                const error = await response.json();
                this.showNotification(`Error: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error stopping background agent:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async updateTask() {
        const agentId = document.getElementById('update-agent-id').value;
        const query = document.getElementById('update-query').value;

        if (!agentId || !query) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        try {
            const response = await fetch('/api/task/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_id: agentId,
                    query: query
                })
            });

            if (response.ok) {
                this.showNotification('Task updated successfully!', 'success');
                this.loadBackgroundAgents();
                document.getElementById('task-update-form').reset();
            } else {
                const error = await response.json();
                this.showNotification(`Error: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error updating task:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async loadTools() {
        try {
            const response = await fetch('/api/tools');
            if (response.ok) {
                const result = await response.json();
                this.displayTools(result.tools || []);
            }
        } catch (error) {
            console.error('Error loading tools:', error);
        }
    }

    displayTools(tools) {
        const container = document.getElementById('tools-grid');
        if (!container) return;

        if (tools.length === 0) {
            container.innerHTML = '<p>No tools available</p>';
            return;
        }

        const html = tools.map(tool => `
            <div class="tool-card">
                <h4>${tool.name}</h4>
                <p>${tool.description || 'No description available'}</p>
                <p><strong>Parameters:</strong> ${tool.parameters ? Object.keys(tool.parameters).join(', ') : 'None'}</p>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async loadEvents() {
        try {
            const response = await fetch('/api/events');
            if (response.ok) {
                const result = await response.json();
                this.displayEvents(result.events || []);
            }
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    displayEvents(events) {
        const container = document.getElementById('events-list');
        if (!container) return;

        if (events.length === 0) {
            container.innerHTML = '<p>No recent events</p>';
            return;
        }

        const html = events.slice(0, 10).map(event => `
            <div class="card">
                <p><strong>${event.type || 'Unknown'}</strong></p>
                <p>${event.message || 'No message'}</p>
                <small>${new Date(event.timestamp).toLocaleString()}</small>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    connectWebSocket() {
        try {
            this.websocket = new WebSocket(`ws://${window.location.host}/ws`);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'ping') {
                        // Handle ping/pong for connection health
                        this.websocket.send(JSON.stringify({type: 'pong', timestamp: new Date().toISOString()}));
                    }
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                // Reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Error connecting WebSocket:', error);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            background: ${type === 'success' ? '#4facfe' : type === 'error' ? '#ff6b6b' : '#f093fb'};
        `;
        
        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// Initialize the interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.omniInterface = new OmniAgentInterface();
});
