/**
 * Sliding Window Algorithm Visualizer
 * Interactive demonstration of sliding window techniques
 */

class SlidingWindowVisualizer {
    constructor() {
        this.elements = [];
        this.currentStep = 0;
        this.maxSteps = 0;
        this.windowSize = 3;
        this.isPlaying = false;
        this.playInterval = null;
        this.algorithm = 'sum';
        this.windowType = 'fixed';
        this.animationSpeed = 1000; // milliseconds
        
        this.initializeEventListeners();
        this.loadExamples();
    }

    initializeEventListeners() {
        // Setup visualization
        document.getElementById('setupVisualization').addEventListener('click', () => {
            this.setupVisualization();
        });

        // Window type change
        document.getElementById('windowType').addEventListener('change', (e) => {
            this.windowType = e.target.value;
            this.toggleWindowSizeInput();
        });

        // Algorithm change
        document.getElementById('algorithm').addEventListener('change', (e) => {
            this.algorithm = e.target.value;
            if (this.elements.length > 0) {
                this.updateVisualization();
            }
        });

        // Control buttons
        document.getElementById('playPause').addEventListener('click', () => {
            this.togglePlayPause();
        });

        document.getElementById('stepForward').addEventListener('click', () => {
            this.stepForward();
        });

        document.getElementById('stepBackward').addEventListener('click', () => {
            this.stepBackward();
        });

        document.getElementById('reset').addEventListener('click', () => {
            this.reset();
        });

        // Speed control
        document.getElementById('speedControl').addEventListener('input', (e) => {
            const speed = parseInt(e.target.value);
            this.animationSpeed = 2000 - (speed * 300); // 1700ms to 500ms
        });

        // Load example
        document.getElementById('loadExample').addEventListener('click', () => {
            this.loadRandomExample();
        });

        // Input validation
        document.getElementById('inputArray').addEventListener('input', () => {
            this.validateInput();
        });

        document.getElementById('windowSize').addEventListener('input', () => {
            this.windowSize = parseInt(document.getElementById('windowSize').value) || 1;
        });
    }

    toggleWindowSizeInput() {
        const container = document.getElementById('windowSizeContainer');
        if (this.windowType === 'variable') {
            container.style.display = 'none';
        } else {
            container.style.display = 'block';
        }
    }

    validateInput() {
        const input = document.getElementById('inputArray').value.trim();
        const setupBtn = document.getElementById('setupVisualization');
        
        if (!input) {
            setupBtn.disabled = true;
            return false;
        }

        try {
            const elements = input.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x));
            if (elements.length === 0) {
                setupBtn.disabled = true;
                return false;
            }
            setupBtn.disabled = false;
            return true;
        } catch (error) {
            setupBtn.disabled = true;
            return false;
        }
    }

    async setupVisualization() {
        const input = document.getElementById('inputArray').value.trim();
        this.algorithm = document.getElementById('algorithm').value;
        this.windowType = document.getElementById('windowType').value;
        this.windowSize = parseInt(document.getElementById('windowSize').value) || 1;

        try {
            // Validate input
            const response = await fetch('/api/validate_input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    input: input,
                    type: 'array'
                })
            });

            const result = await response.json();
            
            if (!result.valid) {
                this.showError(result.error);
                return;
            }

            this.elements = result.parsed;
            this.currentStep = 0;
            
            if (this.windowType === 'fixed') {
                this.maxSteps = Math.max(0, this.elements.length - this.windowSize + 1);
            } else {
                // For variable window, we'll implement specific algorithms later
                this.maxSteps = this.elements.length;
            }

            this.renderVisualization();
            this.updateVisualization();
            
            // Show visualization section
            document.getElementById('visualizationSection').style.display = 'block';
            
        } catch (error) {
            console.error('Error setting up visualization:', error);
            this.showError('Failed to setup visualization');
        }
    }

    renderVisualization() {
        const container = document.getElementById('arrayVisualization');
        container.innerHTML = '';

        this.elements.forEach((element, index) => {
            const elementDiv = document.createElement('div');
            elementDiv.className = 'array-element';
            elementDiv.innerHTML = `
                ${element}
                <div class="index">${index}</div>
                <div class="window-indicator"></div>
            `;
            elementDiv.setAttribute('data-index', index);
            container.appendChild(elementDiv);
        });
    }

    async updateVisualization() {
        // Clear all highlighting
        document.querySelectorAll('.array-element').forEach(el => {
            el.classList.remove('in-window', 'window-start', 'window-end', 'step-animation');
        });

        if (this.windowType === 'fixed') {
            await this.updateFixedWindow();
        } else {
            await this.updateVariableWindow();
        }

        this.updateProgress();
        this.updateControls();
    }

    async updateFixedWindow() {
        if (this.currentStep >= this.maxSteps) {
            return;
        }

        const windowStart = this.currentStep;
        const windowEnd = windowStart + this.windowSize - 1;

        // Highlight window elements
        for (let i = windowStart; i <= windowEnd && i < this.elements.length; i++) {
            const element = document.querySelector(`[data-index="${i}"]`);
            if (element) {
                element.classList.add('in-window');
                if (i === windowStart) element.classList.add('window-start');
                if (i === windowEnd) element.classList.add('window-end');
                
                // Add animation
                setTimeout(() => {
                    element.classList.add('step-animation');
                }, i * 100);
            }
        }

        // Calculate and display result
        try {
            const response = await fetch('/api/calculate_step', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    elements: this.elements,
                    window_start: windowStart,
                    window_size: this.windowSize,
                    algorithm: this.algorithm
                })
            });

            const result = await response.json();
            
            if (result.error) {
                this.showError(result.error);
                return;
            }

            this.displayWindowInfo(result.window, result.result, result.description);
            
        } catch (error) {
            console.error('Error calculating step:', error);
            this.showError('Failed to calculate step result');
        }
    }

    async updateVariableWindow() {
        // Variable window implementation - for now, we'll use a simple expanding window
        const windowEnd = this.currentStep;
        
        // For demonstration, start from index 0 and expand to current step
        for (let i = 0; i <= windowEnd && i < this.elements.length; i++) {
            const element = document.querySelector(`[data-index="${i}"]`);
            if (element) {
                element.classList.add('in-window');
                if (i === 0) element.classList.add('window-start');
                if (i === windowEnd) element.classList.add('window-end');
            }
        }

        // Calculate result for variable window
        const window = this.elements.slice(0, windowEnd + 1);
        let result, description;
        
        switch (this.algorithm) {
            case 'sum':
                result = window.reduce((a, b) => a + b, 0);
                description = `Sum of elements [0-${windowEnd}]: ${window.join(' + ')} = ${result}`;
                break;
            case 'max':
                result = Math.max(...window);
                description = `Maximum in elements [0-${windowEnd}]: max(${window.join(', ')}) = ${result}`;
                break;
            case 'min':
                result = Math.min(...window);
                description = `Minimum in elements [0-${windowEnd}]: min(${window.join(', ')}) = ${result}`;
                break;
            case 'avg':
                result = window.reduce((a, b) => a + b, 0) / window.length;
                description = `Average of elements [0-${windowEnd}]: (${window.join(' + ')}) / ${window.length} = ${result.toFixed(2)}`;
                break;
        }

        this.displayWindowInfo(window, result, description);
    }

    displayWindowInfo(window, result, description) {
        const currentWindowEl = document.getElementById('currentWindow');
        const calculationEl = document.getElementById('calculation');

        currentWindowEl.innerHTML = `
            <strong>Window:</strong> [${window.join(', ')}]<br>
            <strong>Result:</strong> ${result}
        `;

        calculationEl.innerHTML = `
            <div class="calculation-step">${description}</div>
        `;
    }

    updateProgress() {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        const progress = this.maxSteps > 0 ? (this.currentStep / this.maxSteps) * 100 : 0;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `Step ${this.currentStep + 1} of ${this.maxSteps}`;
    }

    updateControls() {
        const stepBackBtn = document.getElementById('stepBackward');
        const stepForwardBtn = document.getElementById('stepForward');
        const playPauseBtn = document.getElementById('playPause');

        stepBackBtn.disabled = this.currentStep <= 0;
        stepForwardBtn.disabled = this.currentStep >= this.maxSteps - 1;

        // Update play/pause button
        if (this.isPlaying) {
            playPauseBtn.innerHTML = '<i class="bi bi-pause"></i> Pause';
            playPauseBtn.className = 'btn btn-warning';
        } else {
            playPauseBtn.innerHTML = '<i class="bi bi-play"></i> Play';
            playPauseBtn.className = 'btn btn-success';
        }
    }

    togglePlayPause() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    play() {
        if (this.currentStep >= this.maxSteps - 1) {
            this.reset();
        }

        this.isPlaying = true;
        this.playInterval = setInterval(() => {
            if (this.currentStep >= this.maxSteps - 1) {
                this.pause();
                return;
            }
            this.stepForward();
        }, this.animationSpeed);

        this.updateControls();
    }

    pause() {
        this.isPlaying = false;
        if (this.playInterval) {
            clearInterval(this.playInterval);
            this.playInterval = null;
        }
        this.updateControls();
    }

    stepForward() {
        if (this.currentStep < this.maxSteps - 1) {
            this.currentStep++;
            this.updateVisualization();
        }
    }

    stepBackward() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateVisualization();
        }
    }

    reset() {
        this.pause();
        this.currentStep = 0;
        this.updateVisualization();
    }

    showError(message) {
        // Create a temporary alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    loadExamples() {
        const examples = [
            {
                title: "Maximum Sum Subarray",
                description: "Find the maximum sum of a subarray of size 3",
                array: "2, 1, 3, 9, 4, 1, 7",
                algorithm: "sum",
                windowSize: 3,
                type: "fixed"
            },
            {
                title: "Moving Average",
                description: "Calculate moving average with window size 4",
                array: "10, 20, 30, 40, 50, 60",
                algorithm: "avg",
                windowSize: 4,
                type: "fixed"
            },
            {
                title: "Maximum in Window",
                description: "Find maximum element in each window of size 3",
                array: "1, 3, 2, 5, 8, 3, 6, 7",
                algorithm: "max",
                windowSize: 3,
                type: "fixed"
            },
            {
                title: "Expanding Window Sum",
                description: "Calculate cumulative sum with expanding window",
                array: "1, 2, 3, 4, 5",
                algorithm: "sum",
                windowSize: 1,
                type: "variable"
            }
        ];

        const container = document.getElementById('examplesContainer');
        container.innerHTML = '';

        examples.forEach((example, index) => {
            const exampleCard = document.createElement('div');
            exampleCard.className = 'col-md-6 col-lg-3 mb-3';
            exampleCard.innerHTML = `
                <div class="card example-card h-100" data-example="${index}">
                    <div class="card-body">
                        <h6 class="card-title">${example.title}</h6>
                        <p class="card-text text-muted small">${example.description}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-secondary">${example.type}</span>
                            <span class="badge bg-primary">${example.algorithm}</span>
                        </div>
                    </div>
                </div>
            `;

            exampleCard.addEventListener('click', () => {
                this.loadExample(example);
            });

            container.appendChild(exampleCard);
        });
    }

    loadExample(example) {
        document.getElementById('inputArray').value = example.array;
        document.getElementById('algorithm').value = example.algorithm;
        document.getElementById('windowType').value = example.type;
        document.getElementById('windowSize').value = example.windowSize;
        
        this.algorithm = example.algorithm;
        this.windowType = example.type;
        this.windowSize = example.windowSize;
        
        this.toggleWindowSizeInput();
        this.validateInput();
    }

    loadRandomExample() {
        const examples = [
            { array: "3, 5, 2, 8, 1, 7, 4", algorithm: "max", windowSize: 3, type: "fixed" },
            { array: "1, 4, 2, 7, 3, 6, 5", algorithm: "sum", windowSize: 2, type: "fixed" },
            { array: "10, 5, 15, 20, 8, 12", algorithm: "avg", windowSize: 3, type: "fixed" },
            { array: "2, 4, 6, 8, 10", algorithm: "min", windowSize: 2, type: "fixed" }
        ];

        const randomExample = examples[Math.floor(Math.random() * examples.length)];
        this.loadExample(randomExample);
    }
}

// Initialize the visualizer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.slidingWindowVisualizer = new SlidingWindowVisualizer();
});
