/**
 * HAITOMAS DASHBOARD — Real-Time WebSocket Client
 */

class HaitomasDashboard {
    constructor() {
        this.ws = null;
        this.commandCount = 0;
        this.startTime = Date.now();

        this.elements = {
            statusText: document.getElementById('status-text'),
            statusIndicator: document.getElementById('status-indicator'),
            cpuStat: document.getElementById('cpu-stat'),
            ramStat: document.getElementById('ram-stat'),
            activityFeed: document.getElementById('activity-feed'),
            chatFeed: document.getElementById('chat-feed'),
            strategyFeed: document.getElementById('strategy-feed'),
            commandInput: document.getElementById('command-input'),
            sendBtn: document.getElementById('send-btn'),
            clearBtn: document.getElementById('clear-activity-btn'),
            totalCommands: document.getElementById('total-commands'),
            uptime: document.getElementById('uptime'),
        };

        this.init();
    }

    init() {
        this.connectWebSocket();
        this.bindEvents();
        this.startUptimeTimer();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.setStatus('ONLINE', false);
                this.addSystemMessage('WebSocket connected to HAITOMAS core.');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };

            this.ws.onclose = () => {
                this.setStatus('DISCONNECTED', true);
                this.addSystemMessage('Connection lost. Reconnecting in 3s...');
                setTimeout(() => this.connectWebSocket(), 3000);
            };

            this.ws.onerror = () => {
                this.setStatus('ERROR', true);
            };
        } catch (e) {
            this.setStatus('OFFLINE', true);
            this.addSystemMessage('WebSocket not available. Using REST API mode.');
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'init':
                this.handleInit(data);
                break;
            case 'update':
                this.handleUpdate(data);
                break;
            case 'command_executed':
                this.handleCommandExecuted(data);
                break;
            case 'error':
                this.handleError(data);
                break;
            case 'stats':
                this.updateStats(data);
                break;
        }
    }

    handleInit(data) {
        if (data.stats) this.updateStats(data.stats);
        if (data.activity) {
            data.activity.forEach(item => this.addActivity(item));
        }
    }

    handleUpdate(data) {
        const panel = data.panel || 'chat';
        if (panel === 'chat') {
            this.addChatMessage(data.text, 'assistant');
        } else if (panel === 'strategy') {
            this.addStrategyItem(data.text);
        }
        this.addActivity(data);
    }

    handleCommandExecuted(data) {
        this.commandCount++;
        this.elements.totalCommands.textContent = `Commands: ${this.commandCount}`;
        this.addActivity({
            type: 'command',
            text: `${data.command}: ${data.result}`,
            time: data.time
        });
    }

    handleError(data) {
        this.addActivity({
            type: 'error',
            text: data.message,
            time: data.time
        });
        this.addChatMessage(`❌ Error: ${data.message}`, 'system');
    }

    updateStats(stats) {
        if (stats.cpu !== undefined) this.elements.cpuStat.textContent = `CPU: ${stats.cpu}%`;
        if (stats.ram !== undefined) this.elements.ramStat.textContent = `RAM: ${stats.ram}%`;
        if (stats.total_commands) {
            this.commandCount = stats.total_commands;
            this.elements.totalCommands.textContent = `Commands: ${stats.total_commands}`;
        }
    }

    setStatus(text, isError) {
        this.elements.statusText.textContent = text;
        if (isError) {
            this.elements.statusIndicator.classList.add('error');
        } else {
            this.elements.statusIndicator.classList.remove('error');
        }
    }

    // ── UI Updates ──

    addActivity(item) {
        const feed = this.elements.activityFeed;
        // Clear empty state
        const empty = feed.querySelector('.empty-state');
        if (empty) empty.remove();

        const div = document.createElement('div');
        div.className = `activity-item ${item.type || ''}`;

        const time = item.time ? new Date(item.time).toLocaleTimeString() : new Date().toLocaleTimeString();
        div.innerHTML = `
            <div class="time">${time}</div>
            <div class="content">${this.escapeHtml(item.text || item.message || '')}</div>
        `;

        feed.appendChild(div);
        feed.scrollTop = feed.scrollHeight;

        // Keep max 100 items
        while (feed.children.length > 100) {
            feed.removeChild(feed.firstChild);
        }
    }

    addChatMessage(text, sender = 'assistant') {
        const feed = this.elements.chatFeed;
        const div = document.createElement('div');
        div.className = `chat-message ${sender}`;

        const labels = { user: 'YOU', assistant: 'HAITOMAS', system: 'SYSTEM' };
        div.innerHTML = `<span class="badge">${labels[sender] || sender.toUpperCase()}</span>${this.escapeHtml(text)}`;

        feed.appendChild(div);
        feed.scrollTop = feed.scrollHeight;
    }

    addStrategyItem(text) {
        const feed = this.elements.strategyFeed;
        const empty = feed.querySelector('.empty-state');
        if (empty) empty.remove();

        const div = document.createElement('div');
        div.className = 'strategy-item';
        div.textContent = text;

        feed.appendChild(div);
        feed.scrollTop = feed.scrollHeight;
    }

    addSystemMessage(text) {
        this.addChatMessage(text, 'system');
    }

    // ── Commands ──

    sendCommand(text) {
        if (!text.trim()) return;

        this.addChatMessage(text, 'user');

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'command', text: text }));
        } else {
            // Fallback to REST
            fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            }).catch(err => {
                this.addSystemMessage('Failed to send command: ' + err.message);
            });
        }
    }

    // ── Events ──

    bindEvents() {
        this.elements.sendBtn.addEventListener('click', () => {
            this.sendCommand(this.elements.commandInput.value);
            this.elements.commandInput.value = '';
        });

        this.elements.commandInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.sendCommand(this.elements.commandInput.value);
                this.elements.commandInput.value = '';
            }
        });

        this.elements.clearBtn.addEventListener('click', () => {
            this.elements.activityFeed.innerHTML = '<div class="empty-state">Activity cleared.</div>';
        });
    }

    startUptimeTimer() {
        setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const hours = Math.floor(elapsed / 3600);
            const minutes = Math.floor((elapsed % 3600) / 60);
            const seconds = elapsed % 60;
            this.elements.uptime.textContent = `Uptime: ${hours}h ${minutes}m ${seconds}s`;
        }, 1000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new HaitomasDashboard();
});
