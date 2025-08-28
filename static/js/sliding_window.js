/**
 * Sliding Window Technique Visualizer
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
        this.animationSpeed = 1500; // milliseconds
        this.windowResults = []; // Track all window results for summary
        
        // Translation helper function
        this.getTranslation = (key) => {
            const currentLang = window.currentLanguage || 'es';
            return window.translations && window.translations[currentLang] && window.translations[currentLang][key] 
                ? window.translations[currentLang][key] 
                : key;
        };
        
        this.initializeEventListeners();
        
        // Load examples after a short delay to ensure translations are ready
        setTimeout(() => {
            this.loadExamples();
        }, 100);
    }

    initializeEventListeners() {
        // Helper function to safely add event listeners
        const safeAddEventListener = (id, event, handler) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener(event, handler);
            }
        };

        // Start visualization demo
        safeAddEventListener('startVisualization', 'click', () => {
            this.startDemo();
        });

        // Window type change
        safeAddEventListener('windowType', 'change', (e) => {
            this.windowType = e.target.value;
            this.toggleWindowSizeInput();
        });

        // Algorithm change
        safeAddEventListener('algorithm', 'change', (e) => {
            this.algorithm = e.target.value;
            this.updateTechniqueInfo();
            this.updateInputMode();
            if (this.elements.length > 0) {
                this.updateVisualization();
            }
        });

        // Speed control
        safeAddEventListener('speedControl', 'input', (e) => {
            const speed = parseInt(e.target.value);
            this.animationSpeed = 2000 - (speed * 300); // 1700ms to 500ms
        });



        // Show code modal
        safeAddEventListener('showCodeBtn', 'click', () => {
            this.showCodeModal();
        });

        // Language change - auto-generate code
        safeAddEventListener('codeLanguage', 'change', () => {
            this.generateCode();
        });

        // Copy code
        safeAddEventListener('copyCodeBtn', 'click', () => {
            this.copyCodeToClipboard();
        });

        // Download code
        safeAddEventListener('downloadCodeBtn', 'click', () => {
            this.downloadCode();
        });

        // Input validation
        safeAddEventListener('inputArray', 'input', () => {
            this.validateInput();
        });

        safeAddEventListener('windowSize', 'input', () => {
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

    updateInputMode() {
        const inputLabel = document.getElementById('inputLabel');
        const inputArray = document.getElementById('inputArray');
        const windowType = document.getElementById('windowType');
        const patternContainer = document.getElementById('patternContainer');
        const windowSizeContainer = document.getElementById('windowSizeContainer');
        
        if (this.algorithm === 'longest_substring') {
            // Switch to string mode for longest substring
            if (inputLabel) {
                inputLabel.textContent = 'Input String';
            }
            if (inputArray) {
                inputArray.placeholder = 'abcabcbb';
                inputArray.value = 'abcabcbb';
            }
            if (windowType) {
                windowType.value = 'variable';
                this.windowType = 'variable';
                this.toggleWindowSizeInput();
            }
            if (patternContainer) {
                patternContainer.style.display = 'none';
            }
        } else if (this.algorithm === 'permutation_in_string') {
            // Switch to string mode with pattern for permutation
            if (inputLabel) {
                inputLabel.textContent = 'Main String';
            }
            if (inputArray) {
                inputArray.placeholder = 'eidbaooo';
                inputArray.value = 'eidbaooo';
            }
            if (windowType) {
                windowType.value = 'fixed';
                this.windowType = 'fixed';
            }
            if (patternContainer) {
                patternContainer.style.display = 'block';
            }
            if (windowSizeContainer) {
                windowSizeContainer.style.display = 'none';
            }
        } else {
            // Switch to array mode
            if (inputLabel) {
                inputLabel.textContent = 'Input Array (comma-separated numbers)';
            }
            if (inputArray) {
                inputArray.placeholder = '1, 2, 3, 4, 5, 6, 7, 8';
                inputArray.value = '1, 2, 3, 4, 5, 6, 7, 8';
            }
            if (windowType) {
                windowType.value = 'fixed';
                this.windowType = 'fixed';
                this.toggleWindowSizeInput();
            }
            if (patternContainer) {
                patternContainer.style.display = 'none';
            }
        }
    }

    validateInput() {
        const input = document.getElementById('inputArray').value.trim();
        const setupBtn = document.getElementById('startVisualization');
        
        if (!input) {
            if (setupBtn) setupBtn.disabled = true;
            return false;
        }

        try {
            if (this.algorithm === 'longest_substring' || this.algorithm === 'permutation_in_string') {
                // For string input, just check if it's not empty
                if (input.length === 0) {
                    if (setupBtn) setupBtn.disabled = true;
                    return false;
                }
            } else {
                // For array input, validate numbers
                const elements = input.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x));
                if (elements.length === 0) {
                    if (setupBtn) setupBtn.disabled = true;
                    return false;
                }
            }
            
            if (setupBtn) setupBtn.disabled = false;
            return true;
        } catch (error) {
            if (setupBtn) setupBtn.disabled = true;
            return false;
        }
    }

    async setupVisualization() {
        const input = document.getElementById('inputArray').value.trim();
        this.algorithm = document.getElementById('algorithm').value;
        this.windowType = document.getElementById('windowType').value;
        this.windowSize = parseInt(document.getElementById('windowSize').value) || 3;

        try {
            // Determine input type based on algorithm
            const inputType = (this.algorithm === 'longest_substring' || this.algorithm === 'permutation_in_string') ? 'string' : 'array';
            
            // For permutation in string, set window size to pattern length
            if (this.algorithm === 'permutation_in_string') {
                const pattern = document.getElementById('patternInput').value.trim();
                this.windowSize = pattern.length;
            }
            
            // Validate input
            const response = await fetch('/api/validate_input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    input: input,
                    type: inputType
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
            
            // Clear previous results summary
            this.clearResultsSummary();
            
            // Show visualization section
            document.getElementById('visualizationSection').style.display = 'block';
            
            // Auto-start the animation
            setTimeout(() => {
                this.play();
            }, 500);
            
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
            // Create element content safely to prevent XSS
            const elementContent = document.createElement('div');
            elementContent.textContent = element;
            elementContent.className = 'element-content';
            
            const indexDiv = document.createElement('div');
            indexDiv.className = 'index';
            indexDiv.textContent = index;
            
            const windowIndicator = document.createElement('div');
            windowIndicator.className = 'window-indicator';
            
            const windowConnection = document.createElement('div');
            windowConnection.className = 'window-connection';
            
            elementDiv.appendChild(elementContent);
            elementDiv.appendChild(indexDiv);
            elementDiv.appendChild(windowIndicator);
            elementDiv.appendChild(windowConnection);
            elementDiv.setAttribute('data-index', index);
            
            // Add staggered animation delay for initial render
            elementDiv.style.animationDelay = `${index * 0.1}s`;
            elementDiv.classList.add('element-fade-in');
            
            container.appendChild(elementDiv);
        });
    }

    async updateVisualization() {
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

        // Clear all previous window styling and labels
        document.querySelectorAll('.array-element').forEach(el => {
            el.classList.remove('in-window', 'window-start', 'window-end');
            // Remove any existing window labels
            const existingLabels = el.querySelectorAll('.window-label');
            existingLabels.forEach(label => label.remove());
        });

        // Wait a brief moment to ensure DOM updates
        await new Promise(resolve => setTimeout(resolve, 50));

        // Apply window styling to current window position
        const elementsToHighlight = [];
        for (let i = windowStart; i <= windowEnd && i < this.elements.length; i++) {
            const element = document.querySelector(`[data-index="${i}"]`);
            if (element) {
                elementsToHighlight.push({element, index: i, isStart: i === windowStart, isEnd: i === windowEnd});
            }
        }

        // Highlight all elements in the window at once
        elementsToHighlight.forEach(({element, index, isStart, isEnd}) => {
            element.classList.add('in-window');
            if (isStart) {
                element.classList.add('window-start');
                this.addWindowLabel(element, 'start');
            }
            if (isEnd) {
                element.classList.add('window-end');
                this.addWindowLabel(element, 'end');
            }
        });



        // Calculate and display result
        try {
            const requestBody = {
                elements: this.elements,
                window_start: windowStart,
                window_size: this.windowSize,
                algorithm: this.algorithm
            };
            
            // Add pattern for permutation in string algorithm
            if (this.algorithm === 'permutation_in_string') {
                const pattern = document.getElementById('patternInput').value.trim();
                requestBody.pattern = pattern;
            }
            
            const response = await fetch('/api/calculate_step', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const result = await response.json();
            
            if (result.error) {
                this.showError(result.error);
                return;
            }

            this.displayWindowInfo(result.window, result.result, result.description);
            
            // Add to results summary
            this.addToResultsSummary(windowStart, result.window, result.result, result.description);
            
        } catch (error) {
            console.error('Error calculating step:', error);
            this.showError('Failed to calculate step result');
        }
    }



    async updateVariableWindow() {
        if (this.algorithm === 'longest_substring') {
            await this.updateLongestSubstringWindow();
            return;
        }
        
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
        
        // Add to results summary
        this.addToResultsSummary(0, window, result, description);
    }

    async updateLongestSubstringWindow() {
        // Initialize sliding window state for longest substring
        if (!this.longestSubstringState) {
            this.longestSubstringState = {
                left: 0,
                right: 0,
                charMap: new Map(),
                maxLength: 0,
                maxStart: 0,
                maxEnd: 0
            };
        }

        const state = this.longestSubstringState;
        
        // Clear all previous styling and labels
        document.querySelectorAll('.array-element').forEach(el => {
            el.classList.remove('in-window', 'window-start', 'window-end');
            // Remove any existing window labels
            const existingLabels = el.querySelectorAll('.window-label');
            existingLabels.forEach(label => label.remove());
        });

        // Advance the algorithm one step
        if (state.right < this.elements.length) {
            const rightChar = this.elements[state.right];
            
            // If character already exists in window, move left pointer
            if (state.charMap.has(rightChar) && state.charMap.get(rightChar) >= state.left) {
                state.left = state.charMap.get(rightChar) + 1;
            }
            
            // Add current character to map
            state.charMap.set(rightChar, state.right);
            
            // Update max length if current window is longer
            const currentLength = state.right - state.left + 1;
            if (currentLength > state.maxLength) {
                state.maxLength = currentLength;
                state.maxStart = state.left;
                state.maxEnd = state.right;
            }
            
            // Highlight current window
            for (let i = state.left; i <= state.right; i++) {
                const element = document.querySelector(`[data-index="${i}"]`);
                if (element) {
                    element.classList.add('in-window');
                    if (i === state.left) element.classList.add('window-start');
                    if (i === state.right) element.classList.add('window-end');
                }
            }
            
            // Show current window and max found so far
            const currentWindow = this.elements.slice(state.left, state.right + 1).join('');
            const maxWindow = this.elements.slice(state.maxStart, state.maxEnd + 1).join('');
            const description = `Current window: "${currentWindow}" (length: ${currentLength})\nLongest so far: "${maxWindow}" (length: ${state.maxLength})`;
            
            this.displayWindowInfo(this.elements.slice(state.left, state.right + 1), state.maxLength, description);
            
            // Add to results summary
            this.addToResultsSummary(state.left, this.elements.slice(state.left, state.right + 1), currentLength, description);
            
            state.right++;
        }
    }

    addToResultsSummary(windowStart, window, result, description) {
        const windowEnd = windowStart + window.length - 1;
        const windowContent = window.join ? window.join('') : window.toString();
        const step = this.currentStep + 1;
        
        // Determine status based on algorithm
        let status = '';
        let statusClass = '';
        
        if (this.algorithm === 'permutation_in_string') {
            if (result === 1) {
                const matchFoundText = this.getTranslation('match-found') || '✓ Match Found';
                status = matchFoundText;
                statusClass = 'text-success';
            } else {
                const noMatchText = this.getTranslation('no-match') || '✗ No Match';
                status = noMatchText;
                statusClass = 'text-muted';
            }
        } else if (this.algorithm === 'longest_substring') {
            if (result > 0) {
                const validText = this.getTranslation('valid') || '✓ Valid';
                status = validText;
                statusClass = 'text-success';
            } else {
                const repeatingText = this.getTranslation('repeating') || '✗ Repeating';
                status = repeatingText;
                statusClass = 'text-warning';
            }
        } else {
            const resultText = this.getTranslation('result-label') || 'Result';
            status = `${resultText}: ${result}`;
            statusClass = 'text-info';
        }
        
        this.windowResults.push({
            step,
            position: `[${windowStart}:${windowEnd}]`,
            content: windowContent,
            result,
            status,
            statusClass
        });
        
        this.updateResultsSummaryTable();
    }

    updateResultsSummaryTable() {
        const summaryTable = document.getElementById('resultsSummary');
        const tableBody = document.getElementById('summaryTableBody');
        
        if (!summaryTable || !tableBody) return;
        
        // Show the table if we have results
        if (this.windowResults.length > 0) {
            summaryTable.style.display = 'block';
        }
        
        // Clear existing rows
        tableBody.innerHTML = '';
        
        // Add rows for each result
        this.windowResults.forEach(result => {
            const row = document.createElement('tr');
            
            // Create cells safely using createElement and textContent
            const stepCell = document.createElement('td');
            stepCell.textContent = result.step;
            
            const positionCell = document.createElement('td');
            const positionCode = document.createElement('code');
            positionCode.textContent = result.position;
            positionCell.appendChild(positionCode);
            
            const contentCell = document.createElement('td');
            const contentCode = document.createElement('code');
            contentCode.textContent = result.content;
            contentCell.appendChild(contentCode);
            
            const resultCell = document.createElement('td');
            resultCell.textContent = result.result;
            
            const statusCell = document.createElement('td');
            statusCell.className = result.statusClass;
            statusCell.textContent = result.status;
            
            row.appendChild(stepCell);
            row.appendChild(positionCell);
            row.appendChild(contentCell);
            row.appendChild(resultCell);
            row.appendChild(statusCell);
            
            tableBody.appendChild(row);
        });
    }

    clearResultsSummary() {
        this.windowResults = [];
        const summaryTable = document.getElementById('resultsSummary');
        const tableBody = document.getElementById('summaryTableBody');
        
        if (summaryTable) {
            summaryTable.style.display = 'none';
        }
        if (tableBody) {
            tableBody.innerHTML = '';
        }
    }

    displayWindowInfo(window, result, description) {
        const currentWindowEl = document.getElementById('currentWindow');
        const calculationEl = document.getElementById('calculation');

        // Use translations for dynamic content
        const windowLabel = this.getTranslation('window');
        const resultLabel = this.getTranslation('result');

        // Safe DOM manipulation to prevent XSS
        currentWindowEl.innerHTML = '';
        
        const windowLabelEl = document.createElement('strong');
        windowLabelEl.textContent = windowLabel + ':';
        
        const windowValuesEl = document.createElement('span');
        windowValuesEl.className = 'window-values';
        windowValuesEl.textContent = '[' + window.join(', ') + ']';
        
        const brEl = document.createElement('br');
        
        const resultLabelEl = document.createElement('strong');
        resultLabelEl.textContent = resultLabel + ':';
        
        const resultValueEl = document.createElement('span');
        resultValueEl.className = 'result-value';
        resultValueEl.textContent = result;
        
        currentWindowEl.appendChild(windowLabelEl);
        currentWindowEl.appendChild(document.createTextNode(' '));
        currentWindowEl.appendChild(windowValuesEl);
        currentWindowEl.appendChild(brEl);
        currentWindowEl.appendChild(resultLabelEl);
        currentWindowEl.appendChild(document.createTextNode(' '));
        currentWindowEl.appendChild(resultValueEl);

        // Translate calculation descriptions
        const translatedDescription = this.translateDescription(description, window, result);
        // Safe DOM manipulation to prevent XSS
        calculationEl.innerHTML = '';
        const calculationStepEl = document.createElement('div');
        calculationStepEl.className = 'calculation-step';
        calculationStepEl.textContent = translatedDescription;
        calculationEl.appendChild(calculationStepEl);

        // Add a subtle celebration effect for results
        const resultElement = currentWindowEl.querySelector('.result-value');
        if (resultElement) {
            resultElement.addEventListener('animationend', () => {
                resultElement.style.animation = '';
            });
        }
    }
    
    translateDescription(description, windowData, result) {
        // Check current language - avoid naming conflict with window parameter
        const currentLang = window.currentLanguage || 'en';
        if (currentLang === 'en') {
            return description; // Return original if English
        }
        
        // Translate descriptions for Spanish
        if (description.includes('Sum of window:')) {
            const sumOfText = this.getTranslation('sum-of-window') || 'Suma de ventana:';
            return description.replace('Sum of window:', sumOfText);
        }
        
        if (description.includes('Maximum in window:')) {
            const maxText = this.getTranslation('max-in-window') || 'Máximo en ventana:';
            return description.replace('Maximum in window:', maxText);
        }
        
        if (description.includes('Minimum in window:')) {
            const minText = this.getTranslation('min-in-window') || 'Mínimo en ventana:';
            return description.replace('Minimum in window:', minText);
        }
        
        if (description.includes('Average of window:')) {
            const avgText = this.getTranslation('avg-of-window') || 'Promedio de ventana:';
            return description.replace('Average of window:', avgText);
        }
        
        return description; // Fallback to original
    }
    
    addWindowLabel(element, type) {
        // Create translatable window label
        const label = document.createElement('div');
        label.className = `window-label ${type}`;
        
        if (type === 'start') {
            label.textContent = this.getTranslation('start-label') || 'START';
        } else if (type === 'end') {
            label.textContent = this.getTranslation('end-label') || 'END';
        }
        
        element.appendChild(label);
    }

    updateProgress() {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        const progress = this.maxSteps > 0 ? (this.currentStep / this.maxSteps) * 100 : 0;
        progressBar.style.width = `${progress}%`;
        const stepText = this.getTranslation('step-progress') || 'Step';
        const ofText = this.getTranslation('of') || 'of';
        progressText.textContent = `${stepText} ${this.currentStep + 1} ${ofText} ${this.maxSteps}`;
    }

    updateControls() {
        const stepBackBtn = document.getElementById('stepBackward');
        const stepForwardBtn = document.getElementById('stepForward');
        const playPauseBtn = document.getElementById('playPause');

        if (stepBackBtn) stepBackBtn.disabled = this.currentStep <= 0;
        if (stepForwardBtn) stepForwardBtn.disabled = this.currentStep >= this.maxSteps - 1;

        // Update play/pause button with translation support
        if (playPauseBtn) {
            const playText = this.getTranslation ? this.getTranslation('play') : 'Play';
            const pauseText = this.getTranslation ? this.getTranslation('pause') : 'Pause';
            
            if (this.isPlaying) {
                playPauseBtn.innerHTML = `<i class="bi bi-pause"></i> ${pauseText}`;
                playPauseBtn.className = 'btn btn-warning';
            } else {
                playPauseBtn.innerHTML = `<i class="bi bi-play"></i> ${playText}`;
                playPauseBtn.className = 'btn btn-success';
            }
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
        // Reset longest substring state for new visualizations
        if (this.longestSubstringState) {
            this.longestSubstringState = null;
        }
        // Clear results summary
        this.clearResultsSummary();
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

    refreshExamples() {
        // Reload examples with current language
        this.loadExamples();
    }

    loadExamples() {
        const examples = [
            {
                titleKey: "example-max-sum-title",
                descKey: "example-max-sum-desc",
                title: "Maximum Sum Subarray",
                description: "Find the maximum sum of a subarray of size 3",
                array: "2, 1, 3, 9, 4, 1, 7",
                algorithm: "sum",
                windowSize: 3,
                type: "fixed"
            },
            {
                titleKey: "example-moving-avg-title",
                descKey: "example-moving-avg-desc",
                title: "Moving Average",
                description: "Calculate moving average with window size 4",
                array: "10, 20, 30, 40, 50, 60",
                algorithm: "avg",
                windowSize: 4,
                type: "fixed"
            },
            {
                titleKey: "example-max-window-title",
                descKey: "example-max-window-desc",
                title: "Maximum in Window",
                description: "Find maximum element in each window of size 3",
                array: "1, 3, 2, 5, 8, 3, 6, 7",
                algorithm: "max",
                windowSize: 3,
                type: "fixed"
            },
            {
                titleKey: "example-expanding-title",
                descKey: "example-expanding-desc",
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
            
            // Use translations if available, otherwise fallback to default text
            const title = this.getTranslation(example.titleKey) || example.title;
            const description = this.getTranslation(example.descKey) || example.description;
            
            exampleCard.innerHTML = `
                <div class="card example-card h-100" data-example="${index}">
                    <div class="card-body">
                        <h6 class="card-title">${title}</h6>
                        <p class="card-text text-muted small">${description}</p>
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

    startDemo() {
        // Use current input if valid, otherwise load a smart example
        const input = document.getElementById('inputArray').value.trim();
        
        if (input && this.validateInput()) {
            // Use the current input
            this.setupVisualization();
        } else {
            // Load a smart example based on current settings
            const algorithm = document.getElementById('algorithm').value;
            const windowType = document.getElementById('windowType').value;
            
            const smartExamples = {
                'fixed': {
                    'sum': { array: "2, 1, 3, 9, 4, 1, 7", windowSize: 3 },
                    'max': { array: "1, 3, 2, 5, 8, 3, 6, 7", windowSize: 3 },
                    'min': { array: "8, 2, 6, 1, 9, 4, 3", windowSize: 3 },
                    'avg': { array: "10, 20, 30, 40, 50, 60", windowSize: 4 }
                },
                'variable': {
                    'sum': { array: "1, 2, 3, 4, 5", windowSize: 1 },
                    'max': { array: "2, 1, 4, 3, 6, 5", windowSize: 1 },
                    'min': { array: "5, 3, 7, 2, 8, 1", windowSize: 1 },
                    'avg': { array: "1, 3, 2, 5, 4, 6", windowSize: 1 }
                }
            };
            
            const example = smartExamples[windowType][algorithm];
            document.getElementById('inputArray').value = example.array;
            document.getElementById('windowSize').value = example.windowSize;
            
            this.setupVisualization();
        }
    }

    showCodeModal() {
        // Show the code generation modal
        const modal = new bootstrap.Modal(document.getElementById('codeModal'));
        modal.show();
        
        // Update algorithm info and generate code immediately
        this.updateTechniqueInfo();
        this.generateCode();
    }

    updateTechniqueInfo() {
        const algorithm = this.algorithm || document.getElementById('algorithm').value;
        const windowType = this.windowType || document.getElementById('windowType').value;
        const windowSize = this.windowSize || parseInt(document.getElementById('windowSize').value);
        
        const algorithmInfo = document.getElementById('algorithmInfo');
        
        const descriptions = {
            'fixed': {
                'sum': `Fixed window sliding technique to find maximum sum of subarray of size ${windowSize}. Time complexity: O(n), Space complexity: O(1).`,
                'max': `Fixed window with deque optimization to find maximum element in each window of size ${windowSize}. Time complexity: O(n), Space complexity: O(k).`,
                'min': `Fixed window with deque optimization to find minimum element in each window of size ${windowSize}. Time complexity: O(n), Space complexity: O(k).`,
                'avg': `Fixed window technique to calculate moving average with window size ${windowSize}. Time complexity: O(n), Space complexity: O(1).`,
                'longest_substring': 'This problem uses variable window - switching to variable mode automatically.',
                'permutation_in_string': 'Fixed window technique to find if any permutation of pattern exists as substring. Uses sliding window with character frequency matching. Time complexity: O(n), Space complexity: O(m) where m is pattern length.'
            },
            'variable': {
                'sum': 'Variable window technique to find subarray with target sum. Time complexity: O(n), Space complexity: O(1).',
                'max': 'Variable window technique to find longest subarray satisfying a condition. Time complexity: O(n²), Space complexity: O(1).',
                'min': 'Variable window technique for minimum window substring problem. Time complexity: O(n + m), Space complexity: O(n + m).',
                'avg': 'Variable window technique to find longest subarray with average above threshold. Time complexity: O(n²), Space complexity: O(1).',
                'longest_substring': 'Variable window technique to find longest substring without repeating characters using sliding window with hash map. Time complexity: O(n), Space complexity: O(min(m,n)) where m is charset size.',
                'permutation_in_string': 'Fixed window technique to find if any permutation of pattern exists as substring. Uses sliding window with character frequency matching. Time complexity: O(n), Space complexity: O(m) where m is pattern length.'
            }
        };
        
        const description = descriptions[windowType]?.[algorithm] || 'Algorithm description not available.';
        // Format algorithm name for display
        const algorithmDisplayNames = {
            'sum': 'Sum',
            'max': 'Maximum',
            'min': 'Minimum', 
            'avg': 'Average',
            'longest_substring': 'Longest Substring',
            'permutation_in_string': 'Permutation in String'
        };
        
        const algorithmDisplay = algorithmDisplayNames[algorithm] || algorithm.toUpperCase();
        algorithmInfo.innerHTML = `<strong>${windowType.charAt(0).toUpperCase() + windowType.slice(1)} Window - ${algorithmDisplay}:</strong> ${description}`;
    }

    async generateCode() {
        const copyBtn = document.getElementById('copyCodeBtn');
        const downloadBtn = document.getElementById('downloadCodeBtn');
        const codeElement = document.getElementById('generatedCode');
        const complexityElement = document.getElementById('complexityInfo');
        
        try {
            const algorithm = document.getElementById('algorithm').value;
            const windowType = document.getElementById('windowType').value;
            const windowSize = parseInt(document.getElementById('windowSize').value);
            const language = document.getElementById('codeLanguage').value;
            
            const response = await fetch('/api/generate_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    algorithm: algorithm,
                    window_type: windowType,
                    window_size: windowSize,
                    language: language
                })
            });
            
            const result = await response.json();
            
            if (result.code) {
                // Display the generated code
                codeElement.textContent = result.code;
                
                // Update complexity information
                const complexityInfo = this.getComplexityInfo(algorithm, windowType);
                complexityElement.textContent = complexityInfo;
                
                // Enable copy and download buttons
                if (copyBtn) copyBtn.disabled = false;
                if (downloadBtn) downloadBtn.disabled = false;
                
                // Store the code for copy/download operations
                this.generatedCode = result.code;
                this.codeLanguage = language;
                this.algorithmName = `${windowType}_window_${algorithm}`;
                
            } else {
                this.showError(result.error || 'Failed to generate code');
                codeElement.textContent = '// Error generating code. Please try again.';
            }
            
        } catch (error) {
            console.error('Error generating code:', error);
            this.showError('Failed to generate code');
            codeElement.textContent = '// Error generating code. Please try again.';
        }
    }

    getComplexityInfo(algorithm, windowType) {
        const complexityMap = {
            'fixed': {
                'sum': 'Time: O(n) - Single pass through array | Space: O(1) - Constant extra space',
                'max': 'Time: O(n) - Amortized linear with deque | Space: O(k) - Deque size bounded by window',
                'min': 'Time: O(n) - Amortized linear with deque | Space: O(k) - Deque size bounded by window',
                'avg': 'Time: O(n) - Single pass through array | Space: O(1) - Constant extra space'
            },
            'variable': {
                'sum': 'Time: O(n) - Two pointers technique | Space: O(1) - Constant extra space',
                'max': 'Time: O(n²) - Nested loops for all subarrays | Space: O(1) - Constant extra space', 
                'min': 'Time: O(n + m) - Linear in string lengths | Space: O(n + m) - Hash maps for character counts',
                'avg': 'Time: O(n²) - Nested loops for all subarrays | Space: O(1) - Constant extra space',
                'longest_substring': 'Time: O(n) - Single pass with sliding window | Space: O(min(m,n)) - Hash map for character positions',
                'permutation_in_string': 'Time: O(n) - Sliding window with frequency matching | Space: O(m) - Character frequency maps'
            }
        };
        
        return complexityMap[windowType]?.[algorithm] || 'Complexity information not available.';
    }

    async copyCodeToClipboard() {
        if (!this.generatedCode) {
            this.showError('No code to copy');
            return;
        }
        
        try {
            await navigator.clipboard.writeText(this.generatedCode);
            
            // Show temporary success message
            const copyBtn = document.getElementById('copyCodeBtn');
            // Store original content safely
            const originalIcon = copyBtn.querySelector('i');
            const originalText = 'Copy Code';
            
            // Update to success state
            copyBtn.innerHTML = '<i class="bi bi-check"></i> Copied!';
            copyBtn.classList.remove('btn-outline-secondary');
            copyBtn.classList.add('btn-success');
            
            setTimeout(() => {
                // Restore original state safely
                copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> ' + originalText;
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-outline-secondary');
            }, 2000);
            
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            this.showError('Failed to copy code to clipboard');
        }
    }

    downloadCode() {
        if (!this.generatedCode) {
            this.showError('No code to download');
            return;
        }
        
        const extensions = {
            'python': 'py',
            'java': 'java',
            'javascript': 'js',
            'cpp': 'cpp'
        };
        
        const extension = extensions[this.codeLanguage] || 'txt';
        const filename = `${this.algorithmName}.${extension}`;
        
        const blob = new Blob([this.generatedCode], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const downloadLink = document.getElementById('downloadCodeBtn');
        downloadLink.href = url;
        downloadLink.download = filename;
        
        // Clean up the URL after download
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 1000);
    }
}

// Initialize the visualizer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.visualizer = new SlidingWindowVisualizer();
});
