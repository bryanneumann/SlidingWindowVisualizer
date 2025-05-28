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

@app.route('/api/generate_code', methods=['POST'])
def generate_code():
    """Generate algorithm code based on current configuration"""
    try:
        data = request.get_json()
        algorithm = data.get('algorithm', 'sum')
        window_type = data.get('window_type', 'fixed')
        window_size = data.get('window_size', 3)
        language = data.get('language', 'python')
        
        code_templates = {
            'python': {
                'fixed': {
                    'sum': f'''def sliding_window_sum(arr, k={window_size}):
    """Find maximum sum of subarray of size k using sliding window"""
    if len(arr) < k:
        return None
    
    # Calculate sum of first window
    window_sum = sum(arr[:k])
    max_sum = window_sum
    
    # Slide the window
    for i in range(len(arr) - k):
        # Remove first element of previous window and add last element of current window
        window_sum = window_sum - arr[i] + arr[i + k]
        max_sum = max(max_sum, window_sum)
    
    return max_sum

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
result = sliding_window_sum(arr, {window_size})
print(f"Maximum sum of subarray of size {window_size}: {{result}}")''',
                    
                    'max': f'''def sliding_window_maximum(arr, k={window_size}):
    """Find maximum element in each window of size k"""
    from collections import deque
    
    if len(arr) < k:
        return []
    
    # Use deque to store indices
    dq = deque()
    result = []
    
    for i in range(len(arr)):
        # Remove elements outside current window
        while dq and dq[0] <= i - k:
            dq.popleft()
        
        # Remove smaller elements from rear
        while dq and arr[dq[-1]] <= arr[i]:
            dq.pop()
        
        dq.append(i)
        
        # Add maximum of current window to result
        if i >= k - 1:
            result.append(arr[dq[0]])
    
    return result

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
result = sliding_window_maximum(arr, {window_size})
print(f"Maximum in each window of size {window_size}: {{result}}")''',
                    
                    'min': f'''def sliding_window_minimum(arr, k={window_size}):
    """Find minimum element in each window of size k"""
    from collections import deque
    
    if len(arr) < k:
        return []
    
    # Use deque to store indices
    dq = deque()
    result = []
    
    for i in range(len(arr)):
        # Remove elements outside current window
        while dq and dq[0] <= i - k:
            dq.popleft()
        
        # Remove larger elements from rear
        while dq and arr[dq[-1]] >= arr[i]:
            dq.pop()
        
        dq.append(i)
        
        # Add minimum of current window to result
        if i >= k - 1:
            result.append(arr[dq[0]])
    
    return result

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
result = sliding_window_minimum(arr, {window_size})
print(f"Minimum in each window of size {window_size}: {{result}}")''',
                    
                    'avg': f'''def sliding_window_average(arr, k={window_size}):
    """Calculate average of each window of size k"""
    if len(arr) < k:
        return []
    
    result = []
    window_sum = sum(arr[:k])
    result.append(window_sum / k)
    
    # Slide the window
    for i in range(len(arr) - k):
        # Remove first element of previous window and add last element of current window
        window_sum = window_sum - arr[i] + arr[i + k]
        result.append(window_sum / k)
    
    return result

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
result = sliding_window_average(arr, {window_size})
print(f"Average of each window of size {window_size}: {{result}}")'''
                },
                'variable': {
                    'sum': '''def variable_window_sum_target(arr, target):
    """Find subarray with sum equal to target using variable window"""
    left = 0
    current_sum = 0
    
    for right in range(len(arr)):
        current_sum += arr[right]
        
        # Shrink window while sum is greater than target
        while current_sum > target and left <= right:
            current_sum -= arr[left]
            left += 1
        
        # Check if we found the target sum
        if current_sum == target:
            return arr[left:right + 1]
    
    return None  # No subarray found

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
target = 15
result = variable_window_sum_target(arr, target)
print(f"Subarray with sum {target}: {result}")''',
                    
                    'max': '''def longest_subarray_with_condition(arr, condition_func):
    """Find longest subarray satisfying a condition using variable window"""
    left = 0
    max_length = 0
    best_window = []
    
    for right in range(len(arr)):
        # Shrink window while condition is not satisfied
        while left <= right and not condition_func(arr[left:right + 1]):
            left += 1
        
        # Update maximum length if current window is valid
        current_length = right - left + 1
        if current_length > max_length:
            max_length = current_length
            best_window = arr[left:right + 1]
    
    return best_window, max_length

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
# Find longest subarray with sum <= 10
condition = lambda window: sum(window) <= 10
result, length = longest_subarray_with_condition(arr, condition)
print(f"Longest subarray with sum <= 10: {result} (length: {length})")''',
                    
                    'min': '''def minimum_window_substring(s, t):
    """Find minimum window substring containing all characters of t"""
    from collections import Counter, defaultdict
    
    if not s or not t or len(s) < len(t):
        return ""
    
    # Count characters in t
    target_count = Counter(t)
    required = len(target_count)
    
    # Sliding window
    left = right = 0
    formed = 0
    window_counts = defaultdict(int)
    
    # Result
    min_len = float('inf')
    min_left = 0
    
    while right < len(s):
        # Add character to window
        char = s[right]
        window_counts[char] += 1
        
        if char in target_count and window_counts[char] == target_count[char]:
            formed += 1
        
        # Contract window
        while left <= right and formed == required:
            # Update result if current window is smaller
            if right - left + 1 < min_len:
                min_len = right - left + 1
                min_left = left
            
            # Remove character from left
            char = s[left]
            window_counts[char] -= 1
            if char in target_count and window_counts[char] < target_count[char]:
                formed -= 1
            
            left += 1
        
        right += 1
    
    return "" if min_len == float('inf') else s[min_left:min_left + min_len]

# Example usage:
s = "ADOBECODEBANC"
t = "ABC"
result = minimum_window_substring(s, t)
print(f"Minimum window substring: {result}")''',
                    
                    'avg': '''def variable_window_average_threshold(arr, threshold):
    """Find longest subarray with average >= threshold using variable window"""
    max_length = 0
    best_window = []
    
    for start in range(len(arr)):
        current_sum = 0
        for end in range(start, len(arr)):
            current_sum += arr[end]
            current_length = end - start + 1
            current_avg = current_sum / current_length
            
            if current_avg >= threshold and current_length > max_length:
                max_length = current_length
                best_window = arr[start:end + 1]
    
    return best_window, max_length

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
threshold = 4.5
result, length = variable_window_average_threshold(arr, threshold)
print(f"Longest subarray with avg >= {threshold}: {result} (length: {length})")'''
                }
            }
        }
        
        # Get the appropriate code template
        if language in code_templates and window_type in code_templates[language]:
            if algorithm in code_templates[language][window_type]:
                code = code_templates[language][window_type][algorithm]
                
                return jsonify({
                    'success': True,
                    'code': code,
                    'language': language,
                    'algorithm': algorithm,
                    'window_type': window_type
                })
        
        return jsonify({'error': 'Code template not found for the specified configuration'})
        
    except Exception as e:
        app.logger.error(f"Error generating code: {str(e)}")
        return jsonify({'error': 'An error occurred while generating code'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
