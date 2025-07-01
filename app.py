import os
import logging
from flask import Flask, render_template, request, jsonify

def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Set up logging - use INFO level for production
log_level = logging.DEBUG if os.environ.get('FLASK_ENV') == 'development' else logging.INFO
logging.basicConfig(level=log_level)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_for_sliding_window")

# Apply security headers to all responses
app.after_request(add_security_headers)

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
        window_start = int(data.get('window_start', 0))
        window_size = int(data.get('window_size', 1))
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
        elif algorithm == 'longest_substring':
            # For longest substring, we need to track the current window and check for duplicates
            window_str = ''.join(window)
            unique_chars = set(window)
            if len(unique_chars) == len(window):
                result = len(window)
                description = f"Window '{window_str}' has no repeating characters. Length: {result}"
            else:
                result = 0
                duplicates = []
                seen = set()
                for char in window:
                    if char in seen:
                        duplicates.append(char)
                    seen.add(char)
                description = f"Window '{window_str}' has repeating characters: {', '.join(set(duplicates))}"
        elif algorithm == 'permutation_in_string':
            # For permutation in string, check if current window is a permutation of the pattern
            window_str = ''.join(window)
            pattern = data.get('pattern', '')
            
            if len(window_str) == len(pattern):
                # Check if window is a permutation of pattern
                from collections import Counter
                window_count = Counter(window_str)
                pattern_count = Counter(pattern)
                
                if window_count == pattern_count:
                    result = 1  # Found permutation
                    description = f"Window '{window_str}' is a permutation of pattern '{pattern}' ✓"
                else:
                    result = 0  # Not a permutation
                    description = f"Window '{window_str}' is not a permutation of pattern '{pattern}'"
            else:
                result = 0
                description = f"Window '{window_str}' (length {len(window_str)}) doesn't match pattern length {len(pattern)}"
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
            'java': {
                'fixed': {
                    'sum': f'''import java.util.*;

public class SlidingWindowSum {{
    public static int maxSumSubarray(int[] arr, int k) {{
        if (arr.length < k) {{
            return -1;
        }}
        
        // Calculate sum of first window
        int windowSum = 0;
        for (int i = 0; i < k; i++) {{
            windowSum += arr[i];
        }}
        int maxSum = windowSum;
        
        // Slide the window
        for (int i = k; i < arr.length; i++) {{
            // Remove first element of previous window and add current element
            windowSum = windowSum - arr[i - k] + arr[i];
            maxSum = Math.max(maxSum, windowSum);
        }}
        
        return maxSum;
    }}
    
    public static void main(String[] args) {{
        int[] arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
        int result = maxSumSubarray(arr, {window_size});
        System.out.println("Maximum sum of subarray of size {window_size}: " + result);
    }}
}}''',
                    
                    'max': f'''import java.util.*;

public class SlidingWindowMaximum {{
    public static List<Integer> maxInWindows(int[] arr, int k) {{
        if (arr.length < k) {{
            return new ArrayList<>();
        }}
        
        Deque<Integer> deque = new ArrayDeque<>();
        List<Integer> result = new ArrayList<>();
        
        for (int i = 0; i < arr.length; i++) {{
            // Remove elements outside current window
            while (!deque.isEmpty() && deque.peekFirst() <= i - k) {{
                deque.pollFirst();
            }}
            
            // Remove smaller elements from rear
            while (!deque.isEmpty() && arr[deque.peekLast()] <= arr[i]) {{
                deque.pollLast();
            }}
            
            deque.offerLast(i);
            
            // Add maximum of current window to result
            if (i >= k - 1) {{
                result.add(arr[deque.peekFirst()]);
            }}
        }}
        
        return result;
    }}
    
    public static void main(String[] args) {{
        int[] arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
        List<Integer> result = maxInWindows(arr, {window_size});
        System.out.println("Maximum in each window of size {window_size}: " + result);
    }}
}}''',
                    
                    'min': f'''import java.util.*;

public class SlidingWindowMinimum {{
    public static List<Integer> minInWindows(int[] arr, int k) {{
        if (arr.length < k) {{
            return new ArrayList<>();
        }}
        
        Deque<Integer> deque = new ArrayDeque<>();
        List<Integer> result = new ArrayList<>();
        
        for (int i = 0; i < arr.length; i++) {{
            // Remove elements outside current window
            while (!deque.isEmpty() && deque.peekFirst() <= i - k) {{
                deque.pollFirst();
            }}
            
            // Remove larger elements from rear
            while (!deque.isEmpty() && arr[deque.peekLast()] >= arr[i]) {{
                deque.pollLast();
            }}
            
            deque.offerLast(i);
            
            // Add minimum of current window to result
            if (i >= k - 1) {{
                result.add(arr[deque.peekFirst()]);
            }}
        }}
        
        return result;
    }}
    
    public static void main(String[] args) {{
        int[] arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
        List<Integer> result = minInWindows(arr, {window_size});
        System.out.println("Minimum in each window of size {window_size}: " + result);
    }}
}}''',
                    
                    'avg': f'''import java.util.*;

public class SlidingWindowAverage {{
    public static List<Double> averageInWindows(int[] arr, int k) {{
        if (arr.length < k) {{
            return new ArrayList<>();
        }}
        
        List<Double> result = new ArrayList<>();
        double windowSum = 0;
        
        // Calculate sum of first window
        for (int i = 0; i < k; i++) {{
            windowSum += arr[i];
        }}
        result.add(windowSum / k);
        
        // Slide the window
        for (int i = k; i < arr.length; i++) {{
            windowSum = windowSum - arr[i - k] + arr[i];
            result.add(windowSum / k);
        }}
        
        return result;
    }}
    
    public static void main(String[] args) {{
        int[] arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
        List<Double> result = averageInWindows(arr, {window_size});
        System.out.println("Average of each window of size {window_size}: " + result);
    }}
}}''',
                    
                    'longest_substring': '''import java.util.*;

public class LongestSubstring {{
    public static int lengthOfLongestSubstring(String s) {{
        Map<Character, Integer> charMap = new HashMap<>();
        int left = 0;
        int maxLength = 0;
        
        for (int right = 0; right < s.length(); right++) {{
            char currentChar = s.charAt(right);
            
            if (charMap.containsKey(currentChar) && charMap.get(currentChar) >= left) {{
                left = charMap.get(currentChar) + 1;
            }}
            
            charMap.put(currentChar, right);
            maxLength = Math.max(maxLength, right - left + 1);
        }}
        
        return maxLength;
    }}
    
    public static void main(String[] args) {{
        String s = "abcabcbb";
        int result = lengthOfLongestSubstring(s);
        System.out.println("Length of longest substring without repeating characters: " + result);
    }}
}}''',
                    
                    'permutation_in_string': '''import java.util.*;

public class PermutationInString {{
    public static boolean checkInclusion(String s1, String s2) {{
        if (s1.length() > s2.length()) {{
            return false;
        }}
        
        Map<Character, Integer> s1Count = new HashMap<>();
        for (char c : s1.toCharArray()) {{
            s1Count.put(c, s1Count.getOrDefault(c, 0) + 1);
        }}
        
        int windowSize = s1.length();
        for (int i = 0; i <= s2.length() - windowSize; i++) {{
            String window = s2.substring(i, i + windowSize);
            Map<Character, Integer> windowCount = new HashMap<>();
            
            for (char c : window.toCharArray()) {{
                windowCount.put(c, windowCount.getOrDefault(c, 0) + 1);
            }}
            
            if (s1Count.equals(windowCount)) {{
                return true;
            }}
        }}
        
        return false;
    }}
    
    public static void main(String[] args) {{
        String s1 = "ab";
        String s2 = "eidbaooo";
        boolean result = checkInclusion(s1, s2);
        System.out.println("Permutation of '" + s1 + "' exists in '" + s2 + "': " + result);
    }}
}}'''
                },
                'variable': {
                    'sum': '''import java.util.*;

public class VariableWindowSum {
    public static int[] subarrayWithSum(int[] arr, int target) {
        int left = 0;
        int currentSum = 0;
        
        for (int right = 0; right < arr.length; right++) {
            currentSum += arr[right];
            
            // Shrink window while sum is greater than target
            while (currentSum > target && left <= right) {
                currentSum -= arr[left];
                left++;
            }
            
            // Check if we found the target sum
            if (currentSum == target) {
                return Arrays.copyOfRange(arr, left, right + 1);
            }
        }
        
        return new int[0]; // No subarray found
    }
    
    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 4, 5, 6, 7, 8};
        int target = 15;
        int[] result = subarrayWithSum(arr, target);
        System.out.println("Subarray with sum " + target + ": " + Arrays.toString(result));
    }
}''',
                    
                    'max': '''import java.util.*;

public class VariableWindowMax {
    public static int[] longestSubarrayWithCondition(int[] arr, int maxSum) {
        int left = 0;
        int maxLength = 0;
        int bestStart = 0, bestEnd = -1;
        
        for (int right = 0; right < arr.length; right++) {
            int currentSum = 0;
            for (int i = left; i <= right; i++) {
                currentSum += arr[i];
            }
            
            // Shrink window while sum exceeds maxSum
            while (currentSum > maxSum && left <= right) {
                left++;
                if (left <= right) {
                    currentSum = 0;
                    for (int i = left; i <= right; i++) {
                        currentSum += arr[i];
                    }
                }
            }
            
            // Update maximum length if current window is valid
            int currentLength = right - left + 1;
            if (currentLength > maxLength) {
                maxLength = currentLength;
                bestStart = left;
                bestEnd = right;
            }
        }
        
        return bestEnd >= bestStart ? Arrays.copyOfRange(arr, bestStart, bestEnd + 1) : new int[0];
    }
    
    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 4, 5, 6, 7, 8};
        int maxSum = 10;
        int[] result = longestSubarrayWithCondition(arr, maxSum);
        System.out.println("Longest subarray with sum <= " + maxSum + ": " + Arrays.toString(result));
    }
}''',
                    
                    'min': '''import java.util.*;

public class MinimumWindowSubstring {
    public static String minWindow(String s, String t) {
        if (s.length() < t.length()) {
            return "";
        }
        
        Map<Character, Integer> targetCount = new HashMap<>();
        for (char c : t.toCharArray()) {
            targetCount.put(c, targetCount.getOrDefault(c, 0) + 1);
        }
        
        int required = targetCount.size();
        int left = 0, right = 0;
        int formed = 0;
        Map<Character, Integer> windowCounts = new HashMap<>();
        
        int minLen = Integer.MAX_VALUE;
        int minLeft = 0;
        
        while (right < s.length()) {
            char character = s.charAt(right);
            windowCounts.put(character, windowCounts.getOrDefault(character, 0) + 1);
            
            if (targetCount.containsKey(character) && 
                windowCounts.get(character).intValue() == targetCount.get(character).intValue()) {
                formed++;
            }
            
            while (left <= right && formed == required) {
                if (right - left + 1 < minLen) {
                    minLen = right - left + 1;
                    minLeft = left;
                }
                
                char leftChar = s.charAt(left);
                windowCounts.put(leftChar, windowCounts.get(leftChar) - 1);
                if (targetCount.containsKey(leftChar) && 
                    windowCounts.get(leftChar) < targetCount.get(leftChar)) {
                    formed--;
                }
                
                left++;
            }
            
            right++;
        }
        
        return minLen == Integer.MAX_VALUE ? "" : s.substring(minLeft, minLeft + minLen);
    }
    
    public static void main(String[] args) {
        String s = "ADOBECODEBANC";
        String t = "ABC";
        String result = minWindow(s, t);
        System.out.println("Minimum window substring: " + result);
    }
}''',
                    
                    'avg': '''import java.util.*;

public class VariableWindowAverage {
    public static int[] longestSubarrayWithAvg(int[] arr, double threshold) {
        int maxLength = 0;
        int bestStart = 0, bestEnd = -1;
        
        for (int start = 0; start < arr.length; start++) {
            int currentSum = 0;
            for (int end = start; end < arr.length; end++) {
                currentSum += arr[end];
                int currentLength = end - start + 1;
                double currentAvg = (double) currentSum / currentLength;
                
                if (currentAvg >= threshold && currentLength > maxLength) {
                    maxLength = currentLength;
                    bestStart = start;
                    bestEnd = end;
                }
            }
        }
        
        return bestEnd >= bestStart ? Arrays.copyOfRange(arr, bestStart, bestEnd + 1) : new int[0];
    }
    
    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 4, 5, 6, 7, 8};
        double threshold = 4.5;
        int[] result = longestSubarrayWithAvg(arr, threshold);
        System.out.println("Longest subarray with avg >= " + threshold + ": " + Arrays.toString(result));
    }
}'''
                }
            },
            'javascript': {
                'fixed': {
                    'sum': f'''function slidingWindowSum(arr, k = {window_size}) {{
    if (arr.length < k) {{
        return null;
    }}
    
    // Calculate sum of first window
    let windowSum = 0;
    for (let i = 0; i < k; i++) {{
        windowSum += arr[i];
    }}
    let maxSum = windowSum;
    
    // Slide the window
    for (let i = k; i < arr.length; i++) {{
        // Remove first element of previous window and add current element
        windowSum = windowSum - arr[i - k] + arr[i];
        maxSum = Math.max(maxSum, windowSum);
    }}
    
    return maxSum;
}}

// Example usage:
const arr = [1, 2, 3, 4, 5, 6, 7, 8];
const result = slidingWindowSum(arr, {window_size});
console.log(`Maximum sum of subarray of size {window_size}: ${{result}}`);''',
                    
                    'max': f'''function slidingWindowMaximum(arr, k = {window_size}) {{
    if (arr.length < k) {{
        return [];
    }}
    
    const deque = [];
    const result = [];
    
    for (let i = 0; i < arr.length; i++) {{
        // Remove elements outside current window
        while (deque.length > 0 && deque[0] <= i - k) {{
            deque.shift();
        }}
        
        // Remove smaller elements from rear
        while (deque.length > 0 && arr[deque[deque.length - 1]] <= arr[i]) {{
            deque.pop();
        }}
        
        deque.push(i);
        
        // Add maximum of current window to result
        if (i >= k - 1) {{
            result.push(arr[deque[0]]);
        }}
    }}
    
    return result;
}}

// Example usage:
const arr = [1, 2, 3, 4, 5, 6, 7, 8];
const result = slidingWindowMaximum(arr, {window_size});
console.log(`Maximum in each window of size {window_size}: ${{result}}`);''',
                    
                    'min': f'''function slidingWindowMinimum(arr, k = {window_size}) {{
    if (arr.length < k) {{
        return [];
    }}
    
    const deque = [];
    const result = [];
    
    for (let i = 0; i < arr.length; i++) {{
        // Remove elements outside current window
        while (deque.length > 0 && deque[0] <= i - k) {{
            deque.shift();
        }}
        
        // Remove larger elements from rear
        while (deque.length > 0 && arr[deque[deque.length - 1]] >= arr[i]) {{
            deque.pop();
        }}
        
        deque.push(i);
        
        // Add minimum of current window to result
        if (i >= k - 1) {{
            result.push(arr[deque[0]]);
        }}
    }}
    
    return result;
}}

// Example usage:
const arr = [1, 2, 3, 4, 5, 6, 7, 8];
const result = slidingWindowMinimum(arr, {window_size});
console.log(`Minimum in each window of size {window_size}: ${{result}}`);''',
                    
                    'avg': f'''function slidingWindowAverage(arr, k = {window_size}) {{
    if (arr.length < k) {{
        return [];
    }}
    
    const result = [];
    let windowSum = 0;
    
    // Calculate sum of first window
    for (let i = 0; i < k; i++) {{
        windowSum += arr[i];
    }}
    result.push(windowSum / k);
    
    // Slide the window
    for (let i = k; i < arr.length; i++) {{
        windowSum = windowSum - arr[i - k] + arr[i];
        result.push(windowSum / k);
    }}
    
    return result;
}}

// Example usage:
const arr = [1, 2, 3, 4, 5, 6, 7, 8];
const result = slidingWindowAverage(arr, {window_size});
console.log(`Average of each window of size {window_size}: ${{result}}`);''',
                    
                    'longest_substring': '''function lengthOfLongestSubstring(s) {
    const charMap = new Map();
    let left = 0;
    let maxLength = 0;
    
    for (let right = 0; right < s.length; right++) {
        const currentChar = s[right];
        
        if (charMap.has(currentChar) && charMap.get(currentChar) >= left) {
            left = charMap.get(currentChar) + 1;
        }
        
        charMap.set(currentChar, right);
        maxLength = Math.max(maxLength, right - left + 1);
    }
    
    return maxLength;
}

// Example usage:
const s = "abcabcbb";
const result = lengthOfLongestSubstring(s);
console.log(`Length of longest substring without repeating characters: ${result}`);''',
                    
                    'permutation_in_string': '''function checkInclusion(s1, s2) {
    if (s1.length > s2.length) {
        return false;
    }
    
    // Count characters in s1
    const s1Count = {};
    for (const char of s1) {
        s1Count[char] = (s1Count[char] || 0) + 1;
    }
    
    const windowSize = s1.length;
    for (let i = 0; i <= s2.length - windowSize; i++) {
        const window = s2.substring(i, i + windowSize);
        const windowCount = {};
        
        for (const char of window) {
            windowCount[char] = (windowCount[char] || 0) + 1;
        }
        
        // Compare character counts
        if (JSON.stringify(s1Count) === JSON.stringify(windowCount)) {
            return true;
        }
    }
    
    return false;
}

// Example usage:
const s1 = "ab";
const s2 = "eidbaooo";
const result = checkInclusion(s1, s2);
console.log(`Permutation of '${s1}' exists in '${s2}': ${result}`);'''
                },
                'variable': {
                    'sum': '''function variableWindowSum(arr, target) {
    let left = 0;
    let currentSum = 0;
    
    for (let right = 0; right < arr.length; right++) {
        currentSum += arr[right];
        
        // Shrink window while sum is greater than target
        while (currentSum > target && left <= right) {
            currentSum -= arr[left];
            left++;
        }
        
        // Check if we found the target sum
        if (currentSum === target) {
            return arr.slice(left, right + 1);
        }
    }
    
    return null; // No subarray found
}

// Example usage:
const arr = [1, 2, 3, 4, 5, 6, 7, 8];
const target = 15;
const result = variableWindowSum(arr, target);
console.log(`Subarray with sum ${target}: ${result}`);''',
                    
                    'max': '''function longestSubarrayWithCondition(arr, maxSum) {
    let left = 0;
    let maxLength = 0;
    let bestWindow = [];
    
    for (let right = 0; right < arr.length; right++) {
        let currentSum = arr.slice(left, right + 1).reduce((a, b) => a + b, 0);
        
        // Shrink window while sum exceeds maxSum
        while (currentSum > maxSum && left <= right) {
            left++;
            if (left <= right) {
                currentSum = arr.slice(left, right + 1).reduce((a, b) => a + b, 0);
            }
        }
        
        // Update maximum length if current window is valid
        const currentLength = right - left + 1;
        if (currentLength > maxLength) {
            maxLength = currentLength;
            bestWindow = arr.slice(left, right + 1);
        }
    }
    
    return bestWindow;
}

// Example usage:
const arr = [1, 2, 3, 4, 5, 6, 7, 8];
const maxSum = 10;
const result = longestSubarrayWithCondition(arr, maxSum);
console.log(`Longest subarray with sum <= ${maxSum}: ${result}`);''',
                    
                    'min': '''function minimumWindowSubstring(s, t) {
    if (s.length < t.length) {
        return "";
    }
    
    const targetCount = {};
    for (const char of t) {
        targetCount[char] = (targetCount[char] || 0) + 1;
    }
    
    const required = Object.keys(targetCount).length;
    let left = 0, right = 0;
    let formed = 0;
    const windowCounts = {};
    
    let minLen = Infinity;
    let minLeft = 0;
    
    while (right < s.length) {
        const character = s[right];
        windowCounts[character] = (windowCounts[character] || 0) + 1;
        
        if (targetCount[character] && windowCounts[character] === targetCount[character]) {
            formed++;
        }
        
        while (left <= right && formed === required) {
            if (right - left + 1 < minLen) {
                minLen = right - left + 1;
                minLeft = left;
            }
            
            const leftChar = s[left];
            windowCounts[leftChar]--;
            if (targetCount[leftChar] && windowCounts[leftChar] < targetCount[leftChar]) {
                formed--;
            }
            
            left++;
        }
        
        right++;
    }
    
    return minLen === Infinity ? "" : s.substring(minLeft, minLeft + minLen);
}

// Example usage:
const s = "ADOBECODEBANC";
const t = "ABC";
const result = minimumWindowSubstring(s, t);
console.log(`Minimum window substring: ${result}`);''',
                    
                    'avg': '''function variableWindowAverageThreshold(arr, threshold) {
    let maxLength = 0;
    let bestWindow = [];
    
    for (let start = 0; start < arr.length; start++) {
        let currentSum = 0;
        for (let end = start; end < arr.length; end++) {
            currentSum += arr[end];
            const currentLength = end - start + 1;
            const currentAvg = currentSum / currentLength;
            
            if (currentAvg >= threshold && currentLength > maxLength) {
                maxLength = currentLength;
                bestWindow = arr.slice(start, end + 1);
            }
        }
    }
    
    return bestWindow;
}

// Example usage:
const arr = [1, 2, 3, 4, 5, 6, 7, 8];
const threshold = 4.5;
const result = variableWindowAverageThreshold(arr, threshold);
console.log(`Longest subarray with avg >= ${threshold}: ${result}`);'''
                }
            },
            'cpp': {
                'fixed': {
                    'sum': f'''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int slidingWindowSum(vector<int>& arr, int k = {window_size}) {{
    if (arr.size() < k) {{
        return -1;
    }}
    
    // Calculate sum of first window
    int windowSum = 0;
    for (int i = 0; i < k; i++) {{
        windowSum += arr[i];
    }}
    int maxSum = windowSum;
    
    // Slide the window
    for (int i = k; i < arr.size(); i++) {{
        // Remove first element of previous window and add current element
        windowSum = windowSum - arr[i - k] + arr[i];
        maxSum = max(maxSum, windowSum);
    }}
    
    return maxSum;
}}

int main() {{
    vector<int> arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
    int result = slidingWindowSum(arr, {window_size});
    cout << "Maximum sum of subarray of size {window_size}: " << result << endl;
    return 0;
}}''',
                    
                    'max': f'''#include <iostream>
#include <vector>
#include <deque>
using namespace std;

vector<int> slidingWindowMaximum(vector<int>& arr, int k = {window_size}) {{
    if (arr.size() < k) {{
        return {{}};
    }}
    
    deque<int> dq;
    vector<int> result;
    
    for (int i = 0; i < arr.size(); i++) {{
        // Remove elements outside current window
        while (!dq.empty() && dq.front() <= i - k) {{
            dq.pop_front();
        }}
        
        // Remove smaller elements from rear
        while (!dq.empty() && arr[dq.back()] <= arr[i]) {{
            dq.pop_back();
        }}
        
        dq.push_back(i);
        
        // Add maximum of current window to result
        if (i >= k - 1) {{
            result.push_back(arr[dq.front()]);
        }}
    }}
    
    return result;
}}

int main() {{
    vector<int> arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
    vector<int> result = slidingWindowMaximum(arr, {window_size});
    cout << "Maximum in each window of size {window_size}: ";
    for (int x : result) cout << x << " ";
    cout << endl;
    return 0;
}}''',
                    
                    'min': f'''#include <iostream>
#include <vector>
#include <deque>
using namespace std;

vector<int> slidingWindowMinimum(vector<int>& arr, int k = {window_size}) {{
    if (arr.size() < k) {{
        return {{}};
    }}
    
    deque<int> dq;
    vector<int> result;
    
    for (int i = 0; i < arr.size(); i++) {{
        // Remove elements outside current window
        while (!dq.empty() && dq.front() <= i - k) {{
            dq.pop_front();
        }}
        
        // Remove larger elements from rear
        while (!dq.empty() && arr[dq.back()] >= arr[i]) {{
            dq.pop_back();
        }}
        
        dq.push_back(i);
        
        // Add minimum of current window to result
        if (i >= k - 1) {{
            result.push_back(arr[dq.front()]);
        }}
    }}
    
    return result;
}}

int main() {{
    vector<int> arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
    vector<int> result = slidingWindowMinimum(arr, {window_size});
    cout << "Minimum in each window of size {window_size}: ";
    for (int x : result) cout << x << " ";
    cout << endl;
    return 0;
}}''',
                    
                    'avg': f'''#include <iostream>
#include <vector>
using namespace std;

vector<double> slidingWindowAverage(vector<int>& arr, int k = {window_size}) {{
    if (arr.size() < k) {{
        return {{}};
    }}
    
    vector<double> result;
    double windowSum = 0;
    
    // Calculate sum of first window
    for (int i = 0; i < k; i++) {{
        windowSum += arr[i];
    }}
    result.push_back(windowSum / k);
    
    // Slide the window
    for (int i = k; i < arr.size(); i++) {{
        windowSum = windowSum - arr[i - k] + arr[i];
        result.push_back(windowSum / k);
    }}
    
    return result;
}}

int main() {{
    vector<int> arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
    vector<double> result = slidingWindowAverage(arr, {window_size});
    cout << "Average of each window of size {window_size}: ";
    for (double x : result) cout << x << " ";
    cout << endl;
    return 0;
}}''',
                    
                    'longest_substring': '''#include <iostream>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

int lengthOfLongestSubstring(string s) {{
    unordered_map<char, int> charMap;
    int left = 0;
    int maxLength = 0;
    
    for (int right = 0; right < s.length(); right++) {{
        char currentChar = s[right];
        
        if (charMap.count(currentChar) && charMap[currentChar] >= left) {{
            left = charMap[currentChar] + 1;
        }}
        
        charMap[currentChar] = right;
        maxLength = max(maxLength, right - left + 1);
    }}
    
    return maxLength;
}}

int main() {{
    string s = "abcabcbb";
    int result = lengthOfLongestSubstring(s);
    cout << "Length of longest substring without repeating characters: " << result << endl;
    return 0;
}}''',
                    
                    'permutation_in_string': '''#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;

bool checkInclusion(string s1, string s2) {{
    if (s1.length() > s2.length()) {{
        return false;
    }}
    
    unordered_map<char, int> s1Count;
    for (char c : s1) {{
        s1Count[c]++;
    }}
    
    int windowSize = s1.length();
    for (int i = 0; i <= s2.length() - windowSize; i++) {{
        string window = s2.substr(i, windowSize);
        unordered_map<char, int> windowCount;
        
        for (char c : window) {{
            windowCount[c]++;
        }}
        
        if (s1Count == windowCount) {{
            return true;
        }}
    }}
    
    return false;
}}

int main() {{
    string s1 = "ab";
    string s2 = "eidbaooo";
    bool result = checkInclusion(s1, s2);
    cout << "Permutation of '" << s1 << "' exists in '" << s2 << "': " << (result ? "true" : "false") << endl;
    return 0;
}}'''
                },
                'variable': {
                    'sum': '''#include <iostream>
#include <vector>
using namespace std;

vector<int> variableWindowSum(vector<int>& arr, int target) {
    int left = 0;
    int currentSum = 0;
    
    for (int right = 0; right < arr.size(); right++) {
        currentSum += arr[right];
        
        // Shrink window while sum is greater than target
        while (currentSum > target && left <= right) {
            currentSum -= arr[left];
            left++;
        }
        
        // Check if we found the target sum
        if (currentSum == target) {
            return vector<int>(arr.begin() + left, arr.begin() + right + 1);
        }
    }
    
    return {}; // No subarray found
}

int main() {
    vector<int> arr = {1, 2, 3, 4, 5, 6, 7, 8};
    int target = 15;
    vector<int> result = variableWindowSum(arr, target);
    cout << "Subarray with sum " << target << ": ";
    for (int x : result) cout << x << " ";
    cout << endl;
    return 0;
}''',
                    
                    'max': '''#include <iostream>
#include <vector>
#include <numeric>
using namespace std;

vector<int> longestSubarrayWithCondition(vector<int>& arr, int maxSum) {
    int left = 0;
    int maxLength = 0;
    vector<int> bestWindow;
    
    for (int right = 0; right < arr.size(); right++) {
        int currentSum = accumulate(arr.begin() + left, arr.begin() + right + 1, 0);
        
        // Shrink window while sum exceeds maxSum
        while (currentSum > maxSum && left <= right) {
            left++;
            if (left <= right) {
                currentSum = accumulate(arr.begin() + left, arr.begin() + right + 1, 0);
            }
        }
        
        // Update maximum length if current window is valid
        int currentLength = right - left + 1;
        if (currentLength > maxLength) {
            maxLength = currentLength;
            bestWindow = vector<int>(arr.begin() + left, arr.begin() + right + 1);
        }
    }
    
    return bestWindow;
}

int main() {
    vector<int> arr = {1, 2, 3, 4, 5, 6, 7, 8};
    int maxSum = 10;
    vector<int> result = longestSubarrayWithCondition(arr, maxSum);
    cout << "Longest subarray with sum <= " << maxSum << ": ";
    for (int x : result) cout << x << " ";
    cout << endl;
    return 0;
}''',
                    
                    'min': '''#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;

string minimumWindowSubstring(string s, string t) {
    if (s.length() < t.length()) {
        return "";
    }
    
    unordered_map<char, int> targetCount;
    for (char c : t) {
        targetCount[c]++;
    }
    
    int required = targetCount.size();
    int left = 0, right = 0;
    int formed = 0;
    unordered_map<char, int> windowCounts;
    
    int minLen = INT_MAX;
    int minLeft = 0;
    
    while (right < s.length()) {
        char character = s[right];
        windowCounts[character]++;
        
        if (targetCount.count(character) && windowCounts[character] == targetCount[character]) {
            formed++;
        }
        
        while (left <= right && formed == required) {
            if (right - left + 1 < minLen) {
                minLen = right - left + 1;
                minLeft = left;
            }
            
            char leftChar = s[left];
            windowCounts[leftChar]--;
            if (targetCount.count(leftChar) && windowCounts[leftChar] < targetCount[leftChar]) {
                formed--;
            }
            
            left++;
        }
        
        right++;
    }
    
    return minLen == INT_MAX ? "" : s.substr(minLeft, minLen);
}

int main() {
    string s = "ADOBECODEBANC";
    string t = "ABC";
    string result = minimumWindowSubstring(s, t);
    cout << "Minimum window substring: " << result << endl;
    return 0;
}''',
                    
                    'avg': '''#include <iostream>
#include <vector>
using namespace std;

vector<int> variableWindowAverageThreshold(vector<int>& arr, double threshold) {
    int maxLength = 0;
    vector<int> bestWindow;
    
    for (int start = 0; start < arr.size(); start++) {
        int currentSum = 0;
        for (int end = start; end < arr.size(); end++) {
            currentSum += arr[end];
            int currentLength = end - start + 1;
            double currentAvg = (double)currentSum / currentLength;
            
            if (currentAvg >= threshold && currentLength > maxLength) {
                maxLength = currentLength;
                bestWindow = vector<int>(arr.begin() + start, arr.begin() + end + 1);
            }
        }
    }
    
    return bestWindow;
}

int main() {
    vector<int> arr = {1, 2, 3, 4, 5, 6, 7, 8};
    double threshold = 4.5;
    vector<int> result = variableWindowAverageThreshold(arr, threshold);
    cout << "Longest subarray with avg >= " << threshold << ": ";
    for (int x : result) cout << x << " ";
    cout << endl;
    return 0;
}'''
                }
            },
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
print(f"Average of each window of size {window_size}: {{result}}")''',
                    
                    'longest_substring': '''def longest_substring_without_repeating(s):
    """Find length of longest substring without repeating characters"""
    char_map = {}
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1
        
        char_map[s[right]] = right
        max_length = max(max_length, right - left + 1)
    
    return max_length

# Example usage:
s = "abcabcbb"
result = longest_substring_without_repeating(s)
print(f"Length of longest substring without repeating characters: {result}")''',
                    
                    'permutation_in_string': '''def check_permutation_in_string(s1, s2):
    """Check if any permutation of s1 exists as substring in s2"""
    from collections import Counter
    
    if len(s1) > len(s2):
        return False
    
    s1_count = Counter(s1)
    window_size = len(s1)
    
    for i in range(len(s2) - window_size + 1):
        window = s2[i:i + window_size]
        if Counter(window) == s1_count:
            return True
    
    return False

# Example usage:
s1 = "ab"
s2 = "eidbaooo"
result = check_permutation_in_string(s1, s2)
print(f"Permutation of '{s1}' exists in '{s2}': {result}")'''
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
