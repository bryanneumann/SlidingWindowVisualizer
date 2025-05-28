import os
import logging
from flask import Flask, render_template, request, jsonify

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_for_sliding_window")

@app.route('/')
def index():
    """Main page with sliding window visualization"""
    return render_template('index.html')

@app.route('/api/validate_input', methods=['POST'])
def validate_input():
    """Validate user input for array/string"""
    try:
        data = request.get_json()
        input_text = data.get('input', '').strip()
        input_type = data.get('type', 'array')
        
        if not input_text:
            return jsonify({'valid': False, 'error': 'Input cannot be empty'})
        
        if input_type == 'array':
            # Try to parse as comma-separated numbers
            try:
                elements = [int(x.strip()) for x in input_text.split(',') if x.strip()]
                if len(elements) == 0:
                    return jsonify({'valid': False, 'error': 'Please enter at least one number'})
                return jsonify({'valid': True, 'parsed': elements})
            except ValueError:
                return jsonify({'valid': False, 'error': 'Please enter valid numbers separated by commas'})
        
        elif input_type == 'string':
            # String input - just validate it's not empty
            if len(input_text) == 0:
                return jsonify({'valid': False, 'error': 'String cannot be empty'})
            return jsonify({'valid': True, 'parsed': list(input_text)})
        
        return jsonify({'valid': False, 'error': 'Invalid input type'})
        
    except Exception as e:
        app.logger.error(f"Error validating input: {str(e)}")
        return jsonify({'valid': False, 'error': 'An error occurred while validating input'})

@app.route('/api/calculate_step', methods=['POST'])
def calculate_step():
    """Calculate the result for a specific window position"""
    try:
        data = request.get_json()
        elements = data.get('elements', [])
        window_start = data.get('window_start', 0)
        window_size = data.get('window_size', 1)
        algorithm = data.get('algorithm', 'sum')
        
        # Validate inputs
        if not elements or window_start < 0 or window_size <= 0:
            return jsonify({'error': 'Invalid parameters'})
        
        if window_start + window_size > len(elements):
            return jsonify({'error': 'Window extends beyond array bounds'})
        
        # Get current window
        window = elements[window_start:window_start + window_size]
        
        # Calculate result based on algorithm
        if algorithm == 'sum':
            result = sum(window)
            description = f"Sum of window: {' + '.join(map(str, window))} = {result}"
        elif algorithm == 'max':
            result = max(window)
            description = f"Maximum in window: max({', '.join(map(str, window))}) = {result}"
        elif algorithm == 'min':
            result = min(window)
            description = f"Minimum in window: min({', '.join(map(str, window))}) = {result}"
        elif algorithm == 'avg':
            result = sum(window) / len(window)
            description = f"Average of window: ({' + '.join(map(str, window))}) / {len(window)} = {result:.2f}"
        else:
            return jsonify({'error': 'Unknown algorithm'})
        
        return jsonify({
            'result': result,
            'window': window,
            'description': description
        })
        
    except Exception as e:
        app.logger.error(f"Error calculating step: {str(e)}")
        return jsonify({'error': 'An error occurred while calculating'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
