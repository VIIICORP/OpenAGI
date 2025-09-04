// Helios Dashboard JavaScript - The Light Interface
document.addEventListener('DOMContentLoaded', () => {
    const connectionStatus = document.getElementById('connection-status');
    const agentStateElement = document.getElementById('agent-state');
    const mainContent = document.getElementById('main-content');
    const welcomeMessage = document.getElementById('welcome');
    const dashboard = document.getElementById('agent-dashboard');
    const currentGoal = document.getElementById('current-goal');
    const goalsProcessed = document.getElementById('goals-processed');
    const uptime = document.getElementById('uptime');
    const memoryStats = document.getElementById('memory-stats');
    const activityLog = document.getElementById('activity-log');
    const currentPlan = document.getElementById('current-plan');
    const executionSteps = document.getElementById('execution-steps');
    const progressFill = document.getElementById('progress-fill');

    let websocket = null;
    let reconnectInterval = null;
    let startTime = null;

    // WebSocket connection
    const wsHost = 'localhost';
    const wsPort = 8765;
    const wsUrl = `ws://${wsHost}:${wsPort}`;

    function connect() {
        try {
            websocket = new WebSocket(wsUrl);

            websocket.onopen = function(event) {
                console.log('Connected to Helios server');
                connectionStatus.textContent = 'CONNECTED';
                connectionStatus.className = 'status connected';
                
                // Show dashboard after connection
                setTimeout(() => {
                    welcomeMessage.style.display = 'none';
                    dashboard.style.display = 'block';
                }, 1000);

                // Clear reconnect interval if it exists
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }

                startTime = Date.now();
                updateUptime();
            };

            websocket.onmessage = function(event) {
                try {
                    const message = JSON.parse(event.data);
                    handleMessage(message);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };

            websocket.onclose = function(event) {
                console.log('Disconnected from Helios server');
                connectionStatus.textContent = 'DISCONNECTED';
                connectionStatus.className = 'status disconnected';
                
                // Show welcome message again
                dashboard.style.display = 'none';
                welcomeMessage.style.display = 'block';

                // Attempt to reconnect
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(() => {
                        console.log('Attempting to reconnect...');
                        connect();
                    }, 5000);
                }
            };

            websocket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };

        } catch (error) {
            console.error('Failed to connect:', error);
            
            // Attempt to reconnect
            if (!reconnectInterval) {
                reconnectInterval = setInterval(() => {
                    console.log('Attempting to reconnect...');
                    connect();
                }, 5000);
            }
        }
    }

    function handleMessage(message) {
        console.log('Received message:', message);

        switch (message.type) {
            case 'connection':
                addActivity(`Connected to Helios: ${message.message}`);
                break;

            case 'agent_status':
                updateAgentStatus(message.data);
                break;

            case 'goal_update':
                updateGoal(message.goal, message.status);
                break;

            case 'plan_update':
                updatePlan(message.plan);
                break;

            case 'execution_update':
                updateExecution(message.step, message.tool, message.result);
                break;

            case 'memory_update':
                updateMemory(message.memory_type, message.operation, message.details);
                break;

            case 'error':
                addActivity(`ERROR: ${message.error}`, 'error');
                break;

            default:
                console.log('Unknown message type:', message.type);
        }
    }

    function updateAgentStatus(data) {
        const state = data.state || 'UNKNOWN';
        
        // Update state indicator
        agentStateElement.textContent = state;
        agentStateElement.className = `state-indicator ${state.toLowerCase()}`;

        // Update statistics
        if (data.goals_processed !== undefined) {
            goalsProcessed.textContent = data.goals_processed;
        }

        // Update current goal
        if (data.current_goal) {
            currentGoal.textContent = data.current_goal.goal || 'Processing...';
        } else {
            currentGoal.textContent = 'No active goal';
        }

        // Update memory stats
        if (data.details && data.details.memory_stats) {
            const stats = data.details.memory_stats;
            memoryStats.textContent = `${stats.short_term_memories || 0}ST / ${stats.long_term_memories || 0}LT`;
        }

        // Add activity
        addActivity(`State changed to ${state}`);
    }

    function updateGoal(goal, status) {
        currentGoal.textContent = goal;
        addActivity(`Goal ${status}: ${goal}`);
        
        // Update progress based on status
        let progress = 0;
        switch (status) {
            case 'received':
                progress = 25;
                break;
            case 'planning':
                progress = 50;
                break;
            case 'executing':
                progress = 75;
                break;
            case 'completed':
                progress = 100;
                break;
        }
        
        progressFill.style.width = `${progress}%`;
    }

    function updatePlan(plan) {
        if (!plan || !plan.plan) {
            currentPlan.innerHTML = '<div class="plan-placeholder">No plan available</div>';
            return;
        }

        let planHtml = '';
        
        // Show directive analysis
        if (plan.directive_analysis) {
            planHtml += '<div class="directive-analysis">';
            planHtml += '<h4>Directive Analysis</h4>';
            for (const [key, value] of Object.entries(plan.directive_analysis)) {
                planHtml += `<p><strong>${key.replace('_', ' ')}:</strong> ${value}</p>`;
            }
            planHtml += '</div>';
        }

        // Show plan steps
        plan.plan.forEach(step => {
            planHtml += `
                <div class="plan-step">
                    <div class="step-header">Step ${step.step}: ${step.description}</div>
                    <div class="step-description">${step.expected_outcome}</div>
                    <div class="step-tool">Tool: ${step.tool}</div>
                </div>
            `;
        });

        currentPlan.innerHTML = planHtml;
        addActivity(`Plan generated with ${plan.plan.length} steps`);
    }

    function updateExecution(step, tool, result) {
        const stepElement = document.createElement('div');
        stepElement.className = `execution-step ${result.success ? 'success' : 'error'}`;
        
        stepElement.innerHTML = `
            <div class="step-header">Step ${step}: ${tool}</div>
            <div class="step-description">Status: ${result.success ? 'Success' : 'Failed'}</div>
            ${result.error ? `<div class="error-message">Error: ${result.error}</div>` : ''}
        `;

        // Replace placeholder or add to existing steps
        if (executionSteps.querySelector('.execution-placeholder')) {
            executionSteps.innerHTML = '';
        }
        
        executionSteps.appendChild(stepElement);
        
        addActivity(`Executed ${tool}: ${result.success ? 'Success' : 'Failed'}`);
    }

    function updateMemory(memoryType, operation, details) {
        addActivity(`Memory ${operation} (${memoryType}): ${details.summary || 'Operation completed'}`);
    }

    function addActivity(message, type = 'info') {
        const activityItem = document.createElement('div');
        activityItem.className = `activity-item new ${type}`;
        activityItem.textContent = `${new Date().toLocaleTimeString()}: ${message}`;

        // Remove placeholder if it exists
        const placeholder = activityLog.querySelector('.activity-item');
        if (placeholder && placeholder.textContent.includes('Waiting for')) {
            activityLog.innerHTML = '';
        }

        // Add to top of log
        activityLog.insertBefore(activityItem, activityLog.firstChild);

        // Keep only last 20 items
        while (activityLog.children.length > 20) {
            activityLog.removeChild(activityLog.lastChild);
        }

        // Remove highlight after animation
        setTimeout(() => {
            activityItem.classList.remove('new');
        }, 2000);
    }

    function updateUptime() {
        if (!startTime) return;

        const uptime_ms = Date.now() - startTime;
        const seconds = Math.floor(uptime_ms / 1000) % 60;
        const minutes = Math.floor(uptime_ms / (1000 * 60)) % 60;
        const hours = Math.floor(uptime_ms / (1000 * 60 * 60));

        uptime.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    // Update uptime every second
    setInterval(updateUptime, 1000);

    // Initialize connection
    connect();

    // Add some demo activity for testing
    setTimeout(() => {
        if (connectionStatus.textContent === 'CONNECTED') {
            addActivity('Dashboard initialized and ready to monitor HUAIMKIND');
        }
    }, 2000);
});

// Add some visual effects
document.addEventListener('mousemove', (e) => {
    // Create a subtle parallax effect
    const elements = document.querySelectorAll('.status-card');
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;

    elements.forEach((el, index) => {
        const speed = (index + 1) * 0.5;
        el.style.transform = `translateX(${x * speed}px) translateY(${y * speed}px)`;
    });
});