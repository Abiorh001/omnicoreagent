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
        this.loadSystemInfo();
        this.connectWebSocket();
        // Begin event streaming as soon as app loads; will attach once session id is known
        this.startEventStream();
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

        // Backend switch controls
        const applyBackendBtn = document.getElementById('apply-backend');
        if (applyBackendBtn) {
            applyBackendBtn.addEventListener('click', async () => {
                const mem = document.getElementById('memory-backend').value;
                const evt = document.getElementById('event-backend').value;
                const status = document.getElementById('backend-status');
                try {
                    await fetch('/api/switch-backend', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'memory', backend: mem }) });
                    await fetch('/api/switch-backend', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'event', backend: evt }) });
                    status.innerHTML = '<span class="success">Backends applied.</span>';
                    this.loadSystemInfo();
                } catch (err) {
                    status.innerHTML = `<span class="error">Failed: ${err.message}</span>`;
                }
            });
        }

        // Background manager status
        const refreshBgBtn = document.getElementById('refresh-bg-status');
        if (refreshBgBtn) {
            refreshBgBtn.addEventListener('click', () => this.loadBackgroundStatus());
        }

        // Events tab controls
        const eventsStart = document.getElementById('events-start');
        const eventsStop = document.getElementById('events-stop');
        if (eventsStart) {
            eventsStart.addEventListener('click', () => this.startEventStream());
        }
        if (eventsStop) {
            eventsStop.addEventListener('click', () => {
                if (this._eventSource) {
                    this._eventSource.close();
                    this._eventSource = null;
                    this.showNotification('Event stream stopped', 'info');
                }
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
                                this.startEventStream(); // Attach live stream for this session
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
                    schedule: schedule
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Background agent created successfully!', 'success');
                this.loadBackgroundAgents(); // Refresh the list
                this.loadSystemInfo(); // Update background agents count
                
                // Clear the form
                document.getElementById('agent-id').value = '';
                document.getElementById('agent-query').value = '';
                document.getElementById('agent-schedule').value = '';
            } else {
                this.showNotification(`Error: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Error creating background agent:', error);
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

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Task updated successfully!', 'success');
                this.loadBackgroundAgents(); // Refresh the list
                this.loadSystemInfo();
                
                // Clear the form
                document.getElementById('update-agent-id').value = '';
                document.getElementById('update-query').value = '';
            } else {
                this.showNotification(`Error: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Error updating task:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async loadTools() {
        try {
            const response = await fetch('/api/tools');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.displayTools(result.tools);
                this.updateToolsSummary(result.tools);
            } else {
                console.error('Failed to load tools:', result.message);
            }
        } catch (error) {
            console.error('Error loading tools:', error);
        }
    }

    displayTools(tools) {
        const container = document.getElementById('tools-grid');
        if (!container) return;

        if (!tools || tools.length === 0) {
            container.innerHTML = '<p>No tools available</p>';
            return;
        }

        const html = tools.map(tool => `
            <div class="tool-card">
                <h4>${tool.name || 'Unnamed Tool'}</h4>
                <p>${tool.description || 'No description available'}</p>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    updateToolsSummary(tools) {
        const container = document.getElementById('tools-summary');
        if (!container) return;

        const count = tools ? tools.length : 0;
        container.innerHTML = `
            <p><strong>${count}</strong> tools available</p>
            <p>Mathematical, text processing, system analysis, and data analysis tools</p>
        `;
    }

    async loadBackgroundAgents() {
        try {
            const response = await fetch('/api/background/list');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.displayBackgroundAgents(result.agents);
            } else {
                console.error('Failed to load background agents:', result.message);
            }
        } catch (error) {
            console.error('Error loading background agents:', error);
        }
    }

    async loadBackgroundStatus() {
        try {
            const response = await fetch('/api/background/status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            const container = document.getElementById('background-status');
            if (result.status === 'success' && container) {
                const m = result.manager || {};
                container.innerHTML = `
                    <div class="system-info-grid">
                        <div class="system-info-item"><h4>Running</h4><div class="value">${m.manager_running ? 'Yes' : 'No'}</div></div>
                        <div class="system-info-item"><h4>Total Agents</h4><div class="value">${m.total_agents || 0}</div></div>
                        <div class="system-info-item"><h4>Scheduled</h4><div class="value">${m.running_agents || 0}</div></div>
                        <div class="system-info-item"><h4>Tasks</h4><div class="value">${m.total_tasks || 0}</div></div>
                        <div class="system-info-item"><h4>Scheduler</h4><div class="value">${m.scheduler_running ? 'Up' : 'Down'}</div></div>
                    </div>
                `;
            }
        } catch (e) {
            console.error('Error loading background status:', e);
        }
    }

    displayBackgroundAgents(agents) {
        const container = document.getElementById('background-agents-list');
        if (!container) return;

        if (!agents || agents.length === 0) {
            container.innerHTML = '<p>No background agents running</p>';
            return;
        }

        const html = agents.map(agent => {
            const interval = agent.interval;
            const schedule = agent.schedule;
            let humanInterval = '';
            if (typeof interval === 'number' && !isNaN(interval) && interval > 0) {
                if (interval % 3600 === 0) humanInterval = `${interval/3600}h`;
                else if (interval % 60 === 0) humanInterval = `${interval/60}m`;
                else humanInterval = `${interval}s`;
            }
            const scheduleLine = (schedule || humanInterval) ? `<small>Schedule: ${schedule || ''} ${humanInterval ? `(${humanInterval})` : ''}</small>` : '';
            const streamBtn = agent.session_id ? `<button class="btn btn-secondary" onclick="window.omniInterface.streamBackground('${agent.session_id}')">View Events</button>` : '';
            return `
            <div class="background-agent-item">
                <h4>${agent.agent_id || 'Unknown Agent'}</h4>
                <p>${agent.query || 'No task description'}</p>
                ${scheduleLine}
                <div class="actions">
                    <button class="btn btn-primary" onclick="window.omniInterface.startAgent('${agent.agent_id}')">Start</button>
                    <button class="btn btn-secondary" onclick="window.omniInterface.pauseAgent('${agent.agent_id}')">Pause</button>
                    <button class="btn btn-secondary" onclick="window.omniInterface.resumeAgent('${agent.agent_id}')">Resume</button>
                    <button class="btn btn-secondary" onclick="window.omniInterface.stopAgent('${agent.agent_id}')">Stop</button>
                    <button class="btn btn-danger" onclick="window.omniInterface.removeAgent('${agent.agent_id}')">Remove</button>
                    ${streamBtn}
                </div>
            </div>`;
        }).join('');

        container.innerHTML = html;
    }

    async startAgent(agentId) {
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

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification(`Agent ${agentId} started successfully!`, 'success');
                this.loadBackgroundAgents(); // Refresh the list
                this.loadSystemInfo();
            } else {
                this.showNotification(`Error: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Error starting agent:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async stopAgent(agentId) {
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

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification(`Agent ${agentId} stopped successfully!`, 'success');
                this.loadBackgroundAgents(); // Refresh the list
                this.loadSystemInfo();
            } else {
                this.showNotification(`Error: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Error stopping agent:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async pauseAgent(agentId) {
        try {
            const response = await fetch('/api/background/pause', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: agentId })
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const result = await response.json();
            if (result.status === 'success') {
                this.showNotification(`Agent ${agentId} paused.`, 'info');
                this.loadBackgroundAgents();
                this.loadSystemInfo();
            } else {
                this.showNotification(`Error: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (e) {
            console.error('Error pausing agent:', e);
            this.showNotification(`Error: ${e.message}`, 'error');
        }
    }

    async resumeAgent(agentId) {
        try {
            const response = await fetch('/api/background/resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: agentId })
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const result = await response.json();
            if (result.status === 'success') {
                this.showNotification(`Agent ${agentId} resumed.`, 'success');
                this.loadBackgroundAgents();
                this.loadSystemInfo();
            } else {
                this.showNotification(`Error: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (e) {
            console.error('Error resuming agent:', e);
            this.showNotification(`Error: ${e.message}`, 'error');
        }
    }

    async removeAgent(agentId) {
        try {
            const response = await fetch(`/api/task/remove/${agentId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification(`Agent ${agentId} removed successfully!`, 'success');
                this.loadBackgroundAgents(); // Refresh the list
                this.loadSystemInfo();
            } else {
                this.showNotification(`Error: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Error removing agent:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }

    async loadEvents() {
        try {
            const qs = this.currentSessionId ? `?session_id=${encodeURIComponent(this.currentSessionId)}` : '';
            const response = await fetch(`/api/events${qs}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.displayEvents(result.events || []);
            } else {
                console.error('Failed to load events:', result.message);
            }
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    startEventStream() {
        if (!this.currentSessionId) return;
        if (this._eventSource) {
            this._eventSource.close();
        }
        const source = new EventSource(`/api/events/stream/${encodeURIComponent(this.currentSessionId)}`);
        const eventsContainer = document.getElementById('events-list');
        source.onmessage = (evt) => {
            try {
                const data = JSON.parse(evt.data);
                if (data.type === 'event' && eventsContainer) {
                    const ev = data.event || {};
                    const type = ev.type || 'event';
                    const agent = ev.agent_name ? ` • ${ev.agent_name}` : '';
                    const ts = ev.timestamp ? new Date(ev.timestamp).toLocaleString() : new Date().toLocaleString();
                    let body = '';
                    if (ev.payload && typeof ev.payload === 'object' && 'message' in ev.payload) {
                        body = ev.payload.message;
                    } else if (ev.payload !== undefined) {
                        try { body = typeof ev.payload === 'string' ? ev.payload : JSON.stringify(ev.payload); } catch { body = String(ev.payload); }
                    } else if (ev.message) {
                        body = ev.message;
                    } else {
                        try { body = JSON.stringify(ev); } catch { body = String(ev); }
                    }
                    const div = document.createElement('div');
                    div.className = 'event-item';
                    div.innerHTML = `<h4>${type}${agent}</h4><p>${body}</p><small>${ts}</small>`;
                    eventsContainer.prepend(div);
                }
            } catch {}
        };
        source.onerror = () => { source.close(); };
        this._eventSource = source;
    }

    streamBackground(sessionId) {
        this.currentSessionId = sessionId;
        this.loadEvents();
        this.startEventStream();
        this.showNotification(`Streaming events for ${sessionId}`, 'info');
        // Switch to events tab if available
        const evTab = document.querySelector('.tab[data-target="events-tab"]');
        if (evTab) evTab.click();
    }

    displayEvents(events) {
        const container = document.getElementById('events-list');
        if (!container) return;

        if (!events || events.length === 0) {
            container.innerHTML = '<p>No recent events</p>';
            return;
        }

        const html = events.slice(0, 10).map(ev => {
            const type = ev.type || 'event';
            const timestamp = ev.timestamp ? new Date(ev.timestamp).toLocaleString() : new Date().toLocaleString();
            const agent = ev.agent_name ? ` • ${ev.agent_name}` : '';
            let body = '';
            if (ev.payload && typeof ev.payload === 'object' && 'message' in ev.payload) {
                body = ev.payload.message;
            } else if (ev.payload !== undefined) {
                try { body = typeof ev.payload === 'string' ? ev.payload : JSON.stringify(ev.payload); } catch { body = String(ev.payload); }
            } else if (ev.message) {
                body = ev.message;
            } else {
                try { body = JSON.stringify(ev); } catch { body = String(ev); }
            }
            return `
            <div class="event-item">
                <h4>${type}${agent}</h4>
                <p>${body}</p>
                <small>${timestamp}</small>
            </div>`;
        }).join('');

        container.innerHTML = html;
    }

    async loadSystemInfo() {
        try {
            const response = await fetch('/api/agent/info');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.displaySystemInfo(result.info);
                this.updateQuickStats(result.info);
                // Prefill backend selectors if present
                const memSel = document.getElementById('memory-backend');
                const evtSel = document.getElementById('event-backend');
                if (memSel && result.info.memory_backend) {
                    memSel.value = result.info.memory_backend;
                }
                if (evtSel && result.info.event_backend) {
                    evtSel.value = result.info.event_backend;
                }
            } else {
                console.error('Failed to load system info:', result.message);
            }
        } catch (error) {
            console.error('Error loading system info:', error);
        }
    }

    displaySystemInfo(info) {
        const container = document.getElementById('system-info');
        if (!container) return;

        container.innerHTML = `
            <div class="system-info-grid">
                <div class="system-info-item">
                    <h4>Agent Name</h4>
                    <div class="value">${info.name || 'Unknown'}</div>
                </div>
                <div class="system-info-item">
                    <h4>Status</h4>
                    <div class="value">${info.status || 'Unknown'}</div>
                </div>
                <div class="system-info-item">
                    <h4>Memory Store</h4>
                    <div class="value">${info.memory_store || 'Unknown'}</div>
                </div>
                <div class="system-info-item">
                    <h4>Event Store</h4>
                    <div class="value">${info.event_store || 'Unknown'}</div>
                </div>
                <div class="system-info-item">
                    <h4>Background Agents</h4>
                    <div class="value">${info.background_agents || 0}</div>
                </div>
                <div class="system-info-item">
                    <h4>Memory Backend</h4>
                    <div class="value">${info.memory_backend || 'Unknown'}</div>
                </div>
                <div class="system-info-item">
                    <h4>Event Backend</h4>
                    <div class="value">${info.event_backend || 'Unknown'}</div>
                </div>
            </div>
        `;
    }

    updateQuickStats(info) {
        const container = document.getElementById('quick-stats');
        if (!container) return;

        container.innerHTML = `
            <p><strong>Status:</strong> ${info.status || 'Unknown'}</p>
            <p><strong>Background Agents:</strong> ${info.background_agents || 0}</p>
            <p><strong>Memory:</strong> ${info.memory_store || 'Unknown'}</p>
        `;
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
