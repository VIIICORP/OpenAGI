// Helios Dashboard JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const connectionStatus = document.getElementById('connection-status');
    const agentStateElement = document.getElementById('agent-state');
    const mainContent = document.getElementById('main-content');
    const welcomeMessage = document.getElementById('welcome');
    
    // Dashboard elements
    const stateCard = document.getElementById('state-card');
    const goalCard = document.getElementById('goal-card');
    const thoughtsCard = document.getElementById('thoughts-card');
    const toolsCard = document.getElementById('tools-card');
    const memoryCard = document.getElementById('memory-card');
    const metricsCard = document.getElementById('metrics-card');
    
    // State elements
    const stateIndicator = document.getElementById('state-indicator');
    const currentState = document.getElementById('current-state');
    const stateMessage = document.getElementById('state-message');
    const lastUpdate = document.getElementById('last-update');
    
    // Goal elements
    const goalText = document.getElementById('goal-text');
    const goalProgress = document.getElementById('goal-progress');
    const goalStatus = document.getElementById('goal-status');
    
    // Stream containers
    const thoughtsContainer = document.getElementById('thoughts-container');
    const toolsContainer = document.getElementById('tools-container');
    const memoryContainer = document.getElementById('memory-container');
    
    // Metrics elements
    const cyclesCount = document.getElementById('cycles-count');
    const goalsCount = document.getElementById('goals-count');
    const successRate = document.getElementById('success-rate');
    const uptime = document.getElementById('uptime');
    const consciousnessLevel = document.getElementById('consciousness-level');
    const activeTools = document.getElementById('active-tools');
    
    let ws = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 10;
    const reconnectDelay = 5000;
    
    // WebSocket connection
    function connectWebSocket() {
        const wsHost = 'localhost';
        const wsPort = 8765;
        const wsUrl = `ws://${wsHost}:${wsPort}`;
        
        try {
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('Connected to Helios server');
                updateConnectionStatus(true);
                reconnectAttempts = 0;
                showDashboard();
            };
            
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };
            
            ws.onclose = () => {
                console.log('Disconnected from Helios server');
                updateConnectionStatus(false);
                
                // Attempt reconnection
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`Reconnection attempt ${reconnectAttempts}/${maxReconnectAttempts}`);
                    setTimeout(connectWebSocket, reconnectDelay);
                } else {
                    console.log('Max reconnection attempts reached');
                    showDisconnectedState();
                }
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            updateConnectionStatus(false);
        }
    }
    
    function updateConnectionStatus(connected) {
        const statusIndicator = connectionStatus.querySelector('.status-indicator');
        const statusText = connectionStatus.querySelector('span');
        
        if (connected) {
            statusIndicator.className = 'status-indicator connected';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Disconnected';
        }
    }
    
    function showDashboard() {
        welcomeMessage.style.display = 'none';
        stateCard.style.display = 'block';
        goalCard.style.display = 'block';
        thoughtsCard.style.display = 'block';
        toolsCard.style.display = 'block';
        memoryCard.style.display = 'block';
        metricsCard.style.display = 'block';
    }
    
    function showDisconnectedState() {
        // Hide dashboard and show welcome message
        welcomeMessage.style.display = 'block';
        stateCard.style.display = 'none';
        goalCard.style.display = 'none';
        thoughtsCard.style.display = 'none';
        toolsCard.style.display = 'none';
        memoryCard.style.display = 'none';
        metricsCard.style.display = 'none';
    }
    
    function handleMessage(data) {
        const messageType = data.type;
        
        switch (messageType) {
            case 'state_update':
                handleStateUpdate(data.data);
                break;
            case 'thought':
                handleThought(data.data);
                break;
            case 'goal_update':
                handleGoalUpdate(data.data);
                break;
            case 'tool_execution':
                handleToolExecution(data.data);
                break;
            case 'memory_update':
                handleMemoryUpdate(data.data);
                break;
            case 'metrics':
                handleMetrics(data.data);
                break;
            case 'error':
                handleError(data.data);
                break;
            default:
                console.log('Unknown message type:', messageType);
        }
    }
    
    function handleStateUpdate(data) {
        const state = data.state;
        const message = data.message || '';
        const timestamp = data.timestamp;
        
        // Update state indicator
        stateIndicator.className = `pulse-circle ${state}`;
        agentStateElement.textContent = state;
        
        // Update state details
        currentState.textContent = state;
        stateMessage.textContent = message;
        lastUpdate.textContent = formatTime(timestamp);
        
        // Update page title
        document.title = `Helios - ${state}`;
        
        console.log(`Agent state: ${state} - ${message}`);
    }
    
    function handleThought(data) {
        const thought = data.content;
        const thoughtType = data.thought_type || 'general';
        const timestamp = data.timestamp;
        
        addToStream(thoughtsContainer, {
            time: formatTime(timestamp),
            content: `[${thoughtType}] ${thought}`,
            className: 'thought-item'
        });
    }
    
    function handleGoalUpdate(data) {
        const goal = data.goal;
        const status = data.status;
        const progress = data.progress || 0;
        
        goalText.textContent = goal;
        goalStatus.textContent = status;
        goalProgress.style.width = `${progress * 100}%`;
    }
    
    function handleToolExecution(data) {
        const toolName = data.tool_name;
        const result = data.result;
        const timestamp = data.timestamp;
        const success = result.success ? '✅' : '❌';
        
        addToStream(toolsContainer, {
            time: formatTime(timestamp),
            toolName: toolName,
            content: `${success} ${result.error || 'Executed successfully'}`,
            className: 'tool-item'
        }, true);
    }
    
    function handleMemoryUpdate(data) {
        const memoryType = data.memory_type;
        const operation = data.operation;
        const content = data.content;
        const timestamp = data.timestamp;
        
        addToStream(memoryContainer, {
            time: formatTime(timestamp),
            type: memoryType,
            content: `${operation}: ${content}`,
            className: 'memory-item'
        }, true);
    }
    
    function handleMetrics(data) {
        const metrics = data.metrics;
        
        if (metrics.cycle_count !== undefined) {
            cyclesCount.textContent = metrics.cycle_count;
        }
        if (metrics.total_goals_processed !== undefined) {
            goalsCount.textContent = metrics.total_goals_processed;
        }
        if (metrics.success_rate !== undefined) {
            successRate.textContent = `${Math.round(metrics.success_rate)}%`;
        }
        if (metrics.uptime !== undefined) {
            uptime.textContent = formatDuration(metrics.uptime);
        }
        if (metrics.consciousness_level !== undefined) {
            consciousnessLevel.textContent = `${Math.round(metrics.consciousness_level)}%`;
        }
        if (metrics.available_tools !== undefined) {
            activeTools.textContent = metrics.available_tools.length || 0;
        }
    }
    
    function handleError(data) {
        const errorMessage = data.message;
        const errorType = data.error_type;
        const timestamp = data.timestamp;
        
        console.error(`Agent error [${errorType}]:`, errorMessage);
        
        // Add to thoughts stream as an error
        addToStream(thoughtsContainer, {
            time: formatTime(timestamp),
            content: `❌ ERROR [${errorType}]: ${errorMessage}`,
            className: 'thought-item error'
        });
    }
    
    function addToStream(container, item, isToolOrMemory = false) {
        const itemElement = document.createElement('div');
        itemElement.className = `${item.className} new-item`;
        
        if (isToolOrMemory && item.toolName) {
            // Tool item
            itemElement.innerHTML = `
                <span class="tool-time">${item.time}</span>
                <span class="tool-name">${item.toolName}</span>
                <span class="tool-result">${item.content}</span>
            `;
        } else if (isToolOrMemory && item.type) {
            // Memory item
            itemElement.innerHTML = `
                <span class="memory-time">${item.time}</span>
                <span class="memory-type">${item.type}</span>
                <span class="memory-operation">${item.content}</span>
            `;
        } else {
            // Thought item
            itemElement.innerHTML = `
                <span class="thought-time">${item.time}</span>
                <span class="thought-content">${item.content}</span>
            `;
        }
        
        // Add to top of container
        container.insertBefore(itemElement, container.firstChild);
        
        // Remove old items if too many
        const maxItems = 20;
        while (container.children.length > maxItems) {
            container.removeChild(container.lastChild);
        }
        
        // Remove animation class after animation
        setTimeout(() => {
            itemElement.classList.remove('new-item');
        }, 300);
    }
    
    function formatTime(timestamp) {
        if (!timestamp) return '--:--:--';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('en-US', { 
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (error) {
            return '--:--:--';
        }
    }
    
    function formatDuration(seconds) {
        if (!seconds || seconds < 0) return '0s';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }
    
    // Periodic status request
    function requestStatus() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'request_status' }));
        }
    }
    
    // Send ping to keep connection alive
    function sendPing() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
        }
    }
    
    // Start connection
    connectWebSocket();
    
    // Set up periodic status requests and pings
    setInterval(requestStatus, 10000); // Every 10 seconds
    setInterval(sendPing, 30000); // Every 30 seconds
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && (!ws || ws.readyState !== WebSocket.OPEN)) {
            console.log('Page became visible, attempting to reconnect...');
            connectWebSocket();
        }
    });
    
    console.log('🌟 Helios dashboard initialized');
});