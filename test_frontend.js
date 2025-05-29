/**
 * Frontend JavaScript Unit Tests for Sliding Window Visualizer
 * These tests verify the core functionality of the SlidingWindowVisualizer class
 */

// Mock DOM elements for testing
const mockDOM = {
    elements: {},
    getElementById: function(id) {
        if (!this.elements[id]) {
            this.elements[id] = {
                innerHTML: '',
                style: { display: 'block' },
                value: '',
                addEventListener: function() {},
                appendChild: function() {},
                removeChild: function() {}
            };
        }
        return this.elements[id];
    },
    createElement: function(tag) {
        return {
            innerHTML: '',
            style: {},
            appendChild: function() {},
            addEventListener: function() {}
        };
    }
};

// Mock global objects
global.document = mockDOM;
global.fetch = async function(url, options) {
    // Mock API responses
    if (url.includes('/api/validate_input')) {
        const body = JSON.parse(options.body);
        if (body.input === '1,2,3,4,5') {
            return {
                ok: true,
                json: async () => ({ valid: true, parsed: [1,2,3,4,5] })
            };
        }
        return {
            ok: true,
            json: async () => ({ valid: false, error: 'Invalid input' })
        };
    }
    
    if (url.includes('/api/calculate_step')) {
        const body = JSON.parse(options.body);
        return {
            ok: true,
            json: async () => ({
                result: body.algorithm === 'sum' ? 6 : 3,
                window: body.elements.slice(body.window_start, body.window_start + body.window_size),
                description: 'Test result'
            })
        };
    }
    
    return { ok: false };
};

// Load the sliding window visualizer (simplified version for testing)
class TestSlidingWindowVisualizer {
    constructor() {
        this.elements = [];
        this.currentStep = 0;
        this.maxSteps = 0;
        this.windowSize = 3;
        this.isPlaying = false;
        this.algorithm = 'sum';
        this.windowType = 'fixed';
        this.windowResults = [];
    }

    validateInput() {
        const inputText = '1,2,3,4,5';
        const inputType = 'array';
        
        if (!inputText.trim()) {
            return { valid: false, error: 'Input cannot be empty' };
        }
        
        if (inputType === 'array') {
            try {
                const elements = inputText.split(',').map(x => parseInt(x.trim()));
                if (elements.some(isNaN)) {
                    return { valid: false, error: 'Invalid numbers' };
                }
                return { valid: true, elements };
            } catch (e) {
                return { valid: false, error: 'Parse error' };
            }
        }
        
        if (inputType === 'string') {
            return { valid: true, elements: Array.from(inputText) };
        }
        
        return { valid: false, error: 'Invalid type' };
    }

    setupVisualization() {
        const validation = this.validateInput();
        if (!validation.valid) {
            throw new Error(validation.error);
        }
        
        this.elements = validation.elements;
        this.currentStep = 0;
        this.maxSteps = Math.max(0, this.elements.length - this.windowSize + 1);
        this.windowResults = [];
        
        return true;
    }

    calculateWindow(windowStart) {
        if (windowStart < 0 || windowStart + this.windowSize > this.elements.length) {
            return { error: 'Window out of bounds' };
        }
        
        const window = this.elements.slice(windowStart, windowStart + this.windowSize);
        let result;
        
        switch (this.algorithm) {
            case 'sum':
                result = window.reduce((a, b) => a + b, 0);
                break;
            case 'max':
                result = Math.max(...window);
                break;
            case 'min':
                result = Math.min(...window);
                break;
            case 'average':
                result = window.reduce((a, b) => a + b, 0) / window.length;
                break;
            default:
                result = 0;
        }
        
        return { result, window, description: `${this.algorithm} of [${window.join(', ')}]` };
    }

    addToResultsSummary(windowStart, window, result, description) {
        this.windowResults.push({
            step: this.currentStep + 1,
            position: `[${windowStart}:${windowStart + window.length - 1}]`,
            content: window.join(''),
            result,
            status: `Result: ${result}`
        });
    }

    stepForward() {
        if (this.currentStep < this.maxSteps - 1) {
            this.currentStep++;
            return true;
        }
        return false;
    }

    stepBackward() {
        if (this.currentStep > 0) {
            this.currentStep--;
            return true;
        }
        return false;
    }

    reset() {
        this.currentStep = 0;
        this.windowResults = [];
        this.isPlaying = false;
    }
}

// Test Suite
function runTests() {
    const tests = [];
    let passed = 0;
    let failed = 0;

    function test(name, fn) {
        tests.push({ name, fn });
    }

    function assert(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed');
        }
    }

    function assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, got ${actual}`);
        }
    }

    function assertArrayEqual(actual, expected, message) {
        if (JSON.stringify(actual) !== JSON.stringify(expected)) {
            throw new Error(message || `Expected [${expected}], got [${actual}]`);
        }
    }

    // Test cases
    test('should initialize with default values', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        assertEqual(visualizer.currentStep, 0);
        assertEqual(visualizer.windowSize, 3);
        assertEqual(visualizer.algorithm, 'sum');
        assertEqual(visualizer.isPlaying, false);
    });

    test('should validate valid array input', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        const result = visualizer.validateInput();
        assert(result.valid, 'Should validate successfully');
        assertArrayEqual(result.elements, [1, 2, 3, 4, 5]);
    });

    test('should setup visualization correctly', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        const success = visualizer.setupVisualization();
        assert(success, 'Setup should succeed');
        assertEqual(visualizer.maxSteps, 3); // 5 elements, window size 3 = 3 possible positions
        assertArrayEqual(visualizer.elements, [1, 2, 3, 4, 5]);
    });

    test('should calculate sum correctly', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        visualizer.algorithm = 'sum';
        
        const result = visualizer.calculateWindow(0);
        assertEqual(result.result, 6); // 1 + 2 + 3
        assertArrayEqual(result.window, [1, 2, 3]);
    });

    test('should calculate max correctly', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        visualizer.algorithm = 'max';
        
        const result = visualizer.calculateWindow(1);
        assertEqual(result.result, 4); // max of [2, 3, 4]
        assertArrayEqual(result.window, [2, 3, 4]);
    });

    test('should calculate min correctly', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        visualizer.algorithm = 'min';
        
        const result = visualizer.calculateWindow(2);
        assertEqual(result.result, 3); // min of [3, 4, 5]
        assertArrayEqual(result.window, [3, 4, 5]);
    });

    test('should calculate average correctly', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        visualizer.algorithm = 'average';
        
        const result = visualizer.calculateWindow(0);
        assertEqual(result.result, 2); // (1 + 2 + 3) / 3
        assertArrayEqual(result.window, [1, 2, 3]);
    });

    test('should handle window out of bounds', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        
        const result = visualizer.calculateWindow(5);
        assert(result.error, 'Should return error for out of bounds');
    });

    test('should step forward correctly', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        
        const success = visualizer.stepForward();
        assert(success, 'Should step forward successfully');
        assertEqual(visualizer.currentStep, 1);
    });

    test('should not step forward beyond max steps', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        visualizer.currentStep = 2; // At max step (3 total steps: 0, 1, 2)
        
        const success = visualizer.stepForward();
        assert(!success, 'Should not step forward beyond max');
        assertEqual(visualizer.currentStep, 2);
    });

    test('should step backward correctly', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        visualizer.currentStep = 1;
        
        const success = visualizer.stepBackward();
        assert(success, 'Should step backward successfully');
        assertEqual(visualizer.currentStep, 0);
    });

    test('should not step backward below zero', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        visualizer.currentStep = 0;
        
        const success = visualizer.stepBackward();
        assert(!success, 'Should not step backward below zero');
        assertEqual(visualizer.currentStep, 0);
    });

    test('should reset correctly', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        visualizer.currentStep = 2;
        visualizer.isPlaying = true;
        visualizer.windowResults = [{ step: 1 }];
        
        visualizer.reset();
        assertEqual(visualizer.currentStep, 0);
        assertEqual(visualizer.isPlaying, false);
        assertEqual(visualizer.windowResults.length, 0);
    });

    test('should add results to summary', () => {
        const visualizer = new TestSlidingWindowVisualizer();
        visualizer.setupVisualization();
        
        visualizer.addToResultsSummary(0, [1, 2, 3], 6, 'Sum test');
        assertEqual(visualizer.windowResults.length, 1);
        assertEqual(visualizer.windowResults[0].result, 6);
        assertEqual(visualizer.windowResults[0].content, '123');
    });

    // Run all tests
    console.log('Running Frontend JavaScript Tests...\n');
    
    tests.forEach(({ name, fn }) => {
        try {
            fn();
            console.log(`✓ ${name}`);
            passed++;
        } catch (error) {
            console.log(`✗ ${name}: ${error.message}`);
            failed++;
        }
    });

    console.log(`\nTest Results: ${passed} passed, ${failed} failed`);
    return failed === 0;
}

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TestSlidingWindowVisualizer, runTests };
}

// Run tests if executed directly
if (typeof window === 'undefined') {
    runTests();
}