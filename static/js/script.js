// JavaScript for Multi-Agent War Simulation web interface

document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI elements
    const numAgentsInput = document.getElementById('num-agents');
    const maxIterationsInput = document.getElementById('max-iterations');
    const healthConfigSelect = document.getElementById('health-config');
    const animProfileSelect = document.getElementById('anim-profile');
    const betaInput = document.getElementById('beta');
    const betaValue = document.getElementById('beta-value');
    const agentTypesContainer = document.getElementById('agent-types-container');
    const runButton = document.getElementById('run-btn');
    const trainButton = document.getElementById('train-btn');
    const statusBadge = document.getElementById('status-badge');
    const loadingSpinner = document.getElementById('loading-spinner');
    const staticPreview = document.getElementById('static-preview');
    const previewImage = document.getElementById('preview-image');
    const animationContainer = document.getElementById('animation-container');
    const infoCollapse = document.getElementById('simulationInfoCollapse');
    
    // RL settings element references
    const learningRateInput = document.getElementById('learning-rate');
    const targetUpdateFrequencyInput = document.getElementById('target-update-frequency');
    const replayBufferSizeInput = document.getElementById('replay-buffer-size');
    const batchSizeInput = document.getElementById('batch-size');
    const initialEpsilonInput = document.getElementById('initial-epsilon');
    const epsilonDecayInput = document.getElementById('epsilon-decay');
    const minEpsilonInput = document.getElementById('min-epsilon');
    const hiddenSizeInput = document.getElementById('hidden-size');
    
    const learningRateValue = document.getElementById('learning-rate-value');
    const targetUpdateFrequencyValue = document.getElementById('target-update-frequency-value');
    const replayBufferSizeValue = document.getElementById('replay-buffer-size-value');
    const batchSizeValue = document.getElementById('batch-size-value');
    const initialEpsilonValue = document.getElementById('initial-epsilon-value');
    const epsilonDecayValue = document.getElementById('epsilon-decay-value');
    const minEpsilonValue = document.getElementById('min-epsilon-value');
    const hiddenSizeValue = document.getElementById('hidden-size-value');
    
    // Store the last animation data for reloading
    let lastAnimationData = null;
    
    // Check if running on local machine
    const isLocalMachine = window.location.hostname === 'localhost' || 
                          window.location.hostname === '127.0.0.1' ||
                          window.location.hostname.startsWith('192.168.') ||
                          window.location.hostname.startsWith('10.') ||
                          window.location.hostname === '';
    
    // If not running locally, disable training functionality (only hide, don't change detection logic)
    if (!isLocalMachine) {
        if (trainButton) {
            trainButton.disabled = true;
            trainButton.title = "Please host the application locally to use RL models";
            // Add a local-only badge with a nicer styling
            const badge = document.createElement('span');
            badge.className = 'badge bg-secondary ms-2';
            badge.textContent = 'Local Only';
            badge.style.fontSize = '0.7rem';
            trainButton.appendChild(badge);
        }
    }
    
    // Initialize tooltips if Bootstrap 5 is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    }
    
    // Add beautiful animation to the page when it loads
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
    
    // Update UI values with smooth transitions
    const updateValue = (element, value) => {
        element.style.transition = 'all 0.3s ease';
        element.textContent = value;
        element.style.transform = 'scale(1.1)';
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 150);
    };
    
    // Update beta value display with animation
    betaInput.addEventListener('input', function() {
        updateValue(betaValue, this.value);
    });
    
    // Event listeners for RL settings inputs with animations
    learningRateInput.addEventListener('input', function() {
        updateValue(learningRateValue, this.value);
    });
    
    targetUpdateFrequencyInput.addEventListener('input', function() {
        updateValue(targetUpdateFrequencyValue, this.value);
    });
    
    replayBufferSizeInput.addEventListener('input', function() {
        updateValue(replayBufferSizeValue, this.value);
    });
    
    batchSizeInput.addEventListener('input', function() {
        updateValue(batchSizeValue, this.value);
    });
    
    initialEpsilonInput.addEventListener('input', function() {
        updateValue(initialEpsilonValue, this.value);
    });
    
    epsilonDecayInput.addEventListener('input', function() {
        updateValue(epsilonDecayValue, this.value);
    });
    
    minEpsilonInput.addEventListener('input', function() {
        updateValue(minEpsilonValue, this.value);
    });
    
    hiddenSizeInput.addEventListener('input', function() {
        updateValue(hiddenSizeValue, this.value);
    });
    
    // Update agent type selectors when number of agents changes
    numAgentsInput.addEventListener('change', updateAgentTypeSelectors);
    
    // Auto-expand the info section on first visit using localStorage
    if (!localStorage.getItem('infoSectionSeen')) {
        setTimeout(() => {
            if (infoCollapse && typeof bootstrap !== 'undefined' && bootstrap.Collapse) {
                new bootstrap.Collapse(infoCollapse).show();
                localStorage.setItem('infoSectionSeen', 'true');
            }
        }, 1000);
    }
    
    // Initialize agent type selectors
    updateAgentTypeSelectors();
    
    // Generate preview image on page load
    generatePreview();
    
    // Run simulation button click handler with animation
    runButton.addEventListener('click', function() {
        animateButtonClick(this);
        runSimulation(false);
    });
    
    // Train and run button click handler with animation
    trainButton.addEventListener('click', function() {
        animateButtonClick(this);
        runSimulation(true);
    });
    
    // Add a nice button click animation
    function animateButtonClick(button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
        }, 150);
    }
    
    // After initializing trainButton:
    trainButton.disabled = true; // Grey out by default
    
    /**
     * Helper to check if any RL agent is selected
     */
    function checkRLAgentSelected() {
        const numAgents = parseInt(numAgentsInput.value);
        const rlSettingsSection = document.getElementById('rl-settings-section');
        let hasRLAgent = false;
        
        // Check if any agent is set to RL
        for (let i = 0; i < numAgents; i++) {
            const select = document.getElementById(`agent-type-${i}`);
            if (select && select.value === 'RL') {
                hasRLAgent = true;
                break;
            }
        }
        
        // Show/hide RL settings and Train button with animation
        if (hasRLAgent) {
            // Show RL settings with fade-in
            rlSettingsSection.style.display = 'block';
            setTimeout(() => {
                rlSettingsSection.style.opacity = '1';
            }, 10);
            
            // Show Train & Run button with fade-in and enable it
            trainButton.style.display = 'block';
            trainButton.disabled = !isLocalMachine; // Only enable if on a local machine
            setTimeout(() => {
                trainButton.style.opacity = '1';
            }, 10);
            
            // Disable the regular Run button when RL agents are present
            runButton.style.transition = 'all 0.3s ease';
            runButton.style.opacity = '0.5';
            runButton.disabled = true;
            runButton.title = "Use 'Train & Run' for RL agents";
            
            // Add a pulsing effect to the Train button to draw attention
            if (!trainButton.classList.contains('pulse-animation')) {
                trainButton.classList.add('pulse-animation');
                setTimeout(() => {
                    trainButton.classList.remove('pulse-animation');
                }, 2000);
            }
        } else {
            // Hide with fade-out
            rlSettingsSection.style.opacity = '0';
            trainButton.style.opacity = '0';
            trainButton.disabled = true;
            
            setTimeout(() => {
                rlSettingsSection.style.display = 'none';
                trainButton.style.display = 'none';
            }, 300); // Match transition time from CSS
            
            // Enable the regular Run button when no RL agents
            runButton.style.transition = 'all 0.3s ease';
            runButton.style.opacity = '1';
            runButton.disabled = false;
            runButton.title = "";
        }
    }
    
    /**
     * Updates the agent type selectors based on the number of agents
     * with improved styling and animations
     */
    function updateAgentTypeSelectors() {
        const numAgents = parseInt(numAgentsInput.value);
        agentTypesContainer.innerHTML = '';
        
        // Default all agents to Random
        const defaultAgentTypes = Array(numAgents).fill("Random");
        
        // Define agent type colors for visual identification
        const agentTypeColors = {
            'RL': 'var(--agent-rl)',
            'Heuristic': 'var(--agent-heuristic)',
            'Random': 'var(--agent-random)'
        };
        
        for (let i = 0; i < numAgents; i++) {
            const agentTypeSelector = document.createElement('div');
            agentTypeSelector.className = 'agent-type-selector';
            agentTypeSelector.style.opacity = '0';
            agentTypeSelector.style.transform = 'translateY(10px)';
            
            const label = document.createElement('label');
            label.textContent = `Agent ${i}:`;
            label.htmlFor = `agent-type-${i}`;
            
            const select = document.createElement('select');
            select.className = 'form-select form-select-sm';
            select.id = `agent-type-${i}`;
            
            const options = [
                { value: 'RL', text: 'RL' },
                { value: 'Heuristic', text: 'Heuristic' },
                { value: 'Random', text: 'Random' }
            ];
            
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.text;
                optionElement.style.color = agentTypeColors[option.value];
                select.appendChild(optionElement);
            });
            
            select.value = defaultAgentTypes[i];
            
            // Add color indicator to the select
            const updateSelectColor = () => {
                select.style.borderLeft = `4px solid ${agentTypeColors[select.value]}`;
            };
            updateSelectColor(); // Initial color
            
            // Add event listener for RL check and color update
            select.addEventListener('change', () => {
                checkRLAgentSelected();
                updateSelectColor();
            });
            
            agentTypeSelector.appendChild(label);
            agentTypeSelector.appendChild(select);
            agentTypesContainer.appendChild(agentTypeSelector);
            
            // Staggered fade-in animation
            setTimeout(() => {
                agentTypeSelector.style.transition = 'all 0.3s ease';
                agentTypeSelector.style.opacity = '1';
                agentTypeSelector.style.transform = 'translateY(0)';
            }, i * 100);
        }
        
        checkRLAgentSelected(); // Initial check
    }
    
    /**
     * Generates a preview image of the simulation
     */
    function generatePreview() {
        // Update the initial message with clear instructions
        const messageElement = staticPreview.querySelector('p');
        messageElement.textContent = "Configure your simulation and click \"Run Simulation\" to start.";
        messageElement.style.fontSize = '16px';
        messageElement.style.padding = '40px 0';
        
        // Add a subtle pulse animation to the run button to draw attention
        setTimeout(() => {
            runButton.classList.add('pulse-once');
            setTimeout(() => {
                runButton.classList.remove('pulse-once');
            }, 1500);
        }, 2000);
        
        // Hide loading spinner and preview image initially
        loadingSpinner.style.display = 'none';
        previewImage.style.display = 'none';
        
        // Set ready status with animation
        setStatus('Ready', 'success');
    }
    
    /**
     * Sets the status badge with animation
     * @param {string} text - Status text to display
     * @param {string} type - Bootstrap contextual class (success, warning, danger, etc.)
     */
    function setStatus(text, type) {
        statusBadge.style.transform = 'scale(0)';
        setTimeout(() => {
            statusBadge.textContent = text;
            statusBadge.className = `badge bg-${type}`;
            statusBadge.style.transform = 'scale(1)';
        }, 200);
    }
    
    // Helper: inject HTML with scripts
    function injectHTMLWithScripts(target, htmlString) {
        // Insert the HTML
        target.innerHTML = htmlString;

        // Reactivate each <script> tag
        target.querySelectorAll('script').forEach(old => {
            const s = document.createElement('script');
            if (old.src)   s.src   = old.src;
            if (old.type)  s.type  = old.type;
            if (old.id)    s.id    = old.id;
            if (old.async) s.async = old.async;
            s.textContent = old.textContent;
            old.replaceWith(s);
        });
        
        // Format end messages better and maintain bar chart size
        setTimeout(() => {
            // Handle end messages
            const endMessages = target.querySelectorAll('.js-plotly-plot + div');
            endMessages.forEach(msg => {
                if (msg.textContent && !msg.classList.contains('end-message')) {
                    msg.className = 'end-message';
                }
            });
            
            // Ensure plotly charts maintain their size
            const plotlyCharts = target.querySelectorAll('.js-plotly-plot');
            plotlyCharts.forEach(chart => {
                chart.style.minHeight = '450px';
                chart.style.width = '100%';
            });
        }, 500);
    }
    
    /**
     * Runs the simulation with current settings
     * @param {boolean} withTraining - Whether to train agents before running
     */
    function runSimulation(withTraining) {
        // Get simulation settings
        const settings = getSimulationSettings();
        
        // Show loading spinner with fade-in
        loadingSpinner.style.opacity = '0';
        loadingSpinner.style.display = 'block';
        setTimeout(() => {
            loadingSpinner.style.transition = 'opacity 0.3s ease';
            loadingSpinner.style.opacity = '1';
        }, 10);
        
        // Hide preview content with fade-out
        staticPreview.style.transition = 'opacity 0.3s ease';
        staticPreview.style.opacity = '0';
        
        // Update status
        setStatus('Processing', 'warning');
        
        // Use the appropriate endpoint based on whether training is needed
        const endpoint = withTraining ? '/train_and_run' : '/run_simulation';
        
        // Send request to server
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || `HTTP error! Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Store animation data for potential reuse
            lastAnimationData = data.animation_html;
            
            // Hide loading spinner with fade-out
            loadingSpinner.style.opacity = '0';
            setTimeout(() => {
                loadingSpinner.style.display = 'none';
            }, 300);
            
            // Show animation container with fade-in
            animationContainer.style.display = 'block';
            animationContainer.style.opacity = '0';
            setTimeout(() => {
                animationContainer.style.transition = 'opacity 0.5s ease';
                animationContainer.style.opacity = '1';
                staticPreview.style.display = 'none';
            }, 10);
            
            // Inject animation HTML with scripts
            injectHTMLWithScripts(animationContainer, data.animation_html);
            
            // Update status
            setStatus('Complete', 'success');
            
            // Scroll to animation if needed
            const rect = animationContainer.getBoundingClientRect();
            if (rect.top < 0 || rect.bottom > window.innerHeight) {
                animationContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            // Add MutationObserver to monitor for end messages and maintain chart size
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.addedNodes.length > 0) {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === 1) { // Element node
                                // Check for end messages
                                if (node.textContent && node.previousElementSibling && 
                                    node.previousElementSibling.classList.contains('js-plotly-plot')) {
                                    node.className = 'end-message';
                                }
                                
                                // Check for plotly charts
                                if (node.classList && node.classList.contains('js-plotly-plot')) {
                                    node.style.minHeight = '450px';
                                    node.style.width = '100%';
                                }
                            }
                        });
                    }
                });
            });
            
            // Start observing the animation container
            observer.observe(animationContainer, { childList: true, subtree: true });
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Hide loading spinner
            loadingSpinner.style.opacity = '0';
            setTimeout(() => {
                loadingSpinner.style.display = 'none';
            }, 300);
            
            // Show preview content again
            staticPreview.style.display = 'block';
            staticPreview.style.opacity = '0';
            setTimeout(() => {
                staticPreview.style.opacity = '1';
            }, 10);
            
            // Update preview message with specific error
            const messageElement = staticPreview.querySelector('p');
            messageElement.textContent = `Error: ${error.message || "Error processing simulation. Please try again."}`;
            messageElement.style.color = 'var(--danger)';
            
            // Update status
            setStatus('Error', 'danger');
        });
    }
    
    /**
     * Gets all current simulation settings from the form
     * @returns {Object} The simulation settings
     */
    function getSimulationSettings() {
        // Get basic settings
        const numAgents = parseInt(numAgentsInput.value);
        const maxIteration = maxIterationsInput ? parseInt(maxIterationsInput.value) : 1000;
        const healthConfig = parseInt(healthConfigSelect.value);
        const animProfile = parseInt(animProfileSelect.value);
        const beta = parseFloat(betaInput.value);
        
        // Get agent types
        const agentTypes = [];
        for (let i = 0; i < numAgents; i++) {
            const select = document.getElementById(`agent-type-${i}`);
            agentTypes.push(select ? select.value : 'Random');
        }
        
        // Get RL settings if they exist
        const settings = {
            num_agents: numAgents,
            max_iteration: maxIteration,
            health_config: healthConfig,
            anim_profile: animProfile,
            beta: beta,
            agent_types: agentTypes
        };
        
        // Add RL settings if they exist
        if (learningRateInput) settings.learning_rate = parseFloat(learningRateInput.value);
        if (targetUpdateFrequencyInput) settings.target_update_frequency = parseInt(targetUpdateFrequencyInput.value);
        if (replayBufferSizeInput) settings.replay_buffer_size = parseInt(replayBufferSizeInput.value);
        if (batchSizeInput) settings.batch_size = parseInt(batchSizeInput.value);
        if (initialEpsilonInput) settings.initial_epsilon = parseFloat(initialEpsilonInput.value);
        if (epsilonDecayInput) settings.epsilon_decay = parseFloat(epsilonDecayInput.value);
        if (minEpsilonInput) settings.min_epsilon = parseFloat(minEpsilonInput.value);
        if (hiddenSizeInput) settings.hidden_size = parseInt(hiddenSizeInput.value);
        
        return settings;
    }
    
    // Add favicon dynamically to prevent 404 errors
    function addFavicon() {
        const head = document.head;
        const link = document.createElement('link');
        link.type = 'image/x-icon';
        link.rel = 'shortcut icon';
        link.href = 'data:image/x-icon;base64,AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMZNDGDGTQyPxk0Mj8ZNDEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADGTQzfxk0M/8ZNDP/GTQz/xk0MjwAAAAAAAAAAxk0MEMZNDGDGTQxgxk0MEAAAAAAAAAAAAAAAAAAAAADGTQxgxk0M/8ZNDP/GTQz/xk0M/8ZNDGAAAAAAAAAAAAAAAADGTQzPxk0M/8ZNDP/GTQzPAAAAAAAAAADGTQwgxk0M/8ZNDP/GTQz/xk0M/8ZNDP/GTQxgAAAAAAAAAAAAAAAAAAAAAMZNDN/GTQz/xk0M38ZNDJ/GTQzfxk0M/8ZNDP/GTQz/xk0M/8ZNDP/GTQz/xk0MYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMZNDFDGTQz/xk0M/8ZNDP/GTQz/xk0M/8ZNDP/GTQz/xk0M/8ZNDGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADGTQwQxk0M78ZNDP/GTQz/xk0M/8ZNDP/GTQz/xk0M/8ZNDP/GTQxgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxk0M38ZNDP/GTQz/xk0M/8ZNDP/GTQxgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMZNDCDGTQzPxk0MUMZNDP/GTQz/xk0MYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////EMhQERD///8QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxk0MAMZNDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADGTQwAxk0MAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//8AAP//AAD//wAA7/8AAMf/AADn/wAAw/8AAMf/AADH/wAAx/8AAPf/AAD//wAA//8AAP//AAD//wAA//8AAA==';
        head.appendChild(link);
    }
    
    // Add Apple touch icon dynamically
    function addAppleTouchIcon() {
        const head = document.head;
        const link = document.createElement('link');
        link.rel = 'apple-touch-icon';
        link.href = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAALEwEAmpwYAAABVklEQVQ4y52TzW3CUBCF3xvDF04pAcpGEaICSsjONXBJB6QDsgN2QgkuYeNeVkAFKQFOwCGHHTQ/CiLBIs/ZM09v3puZJ/zRdF1/sNbOiGgihDi5HhG1lVLLLMt+7jW/BQRBkEgpP51zhRDCA6CcNQDVzNw45xaMsRVjbNVqtbbNZjPL8/xYlmXhAQAIrLWfRJQR0ZiIfq21n51O56nX683LshxyzseO41UURbuiKA4+gMjvjDG2nhpjZkmS5Mx9/NFRSi0dx5t/AXmeH51z00aj8ToajbZ5nv9alnd2EfnCQc65hef5I8dx7s5ijHkXQhxqtdr2agXXAsdxvsFgsCeiIREZpdSOc74/A64NADgRkY6i6KUHYIwdrbUzAG0AJoqi3WAw2F8Do9HoKwzDJM/zYxiGyWQy2YVhuHHO2avJRFQrpZZJkuTNZjNzXXcjpdwQUQtAVVXVqVar3a/stH8CLeAbs20VprIAAAAASUVORK5CYII=';
        head.appendChild(link);
    }
    
    // Call the favicon functions to prevent 404 errors
    addFavicon();
    addAppleTouchIcon();
});

// Add CSS animations for buttons
document.head.insertAdjacentHTML('beforeend', `
<style>
.pulse-animation {
    animation: pulse 1.5s infinite;
}

.pulse-once {
    animation: pulse 1.5s 1;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(99, 102, 241, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
    }
}
</style>
`); 