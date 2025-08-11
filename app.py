import os
import logging
import time
import hashlib
import ipaddress
import requests
from collections import defaultdict, deque
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Rate limiting for geo-blocking to prevent spam
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(deque)
        self.redirected_ips = defaultdict(float)
    
    def is_rate_limited(self, ip, max_requests=5, window_minutes=60):
        """Check if IP is rate limited for geo-blocking"""
        now = time.time()
        window_seconds = window_minutes * 60
        
        # Clean old entries
        while self.requests[ip] and self.requests[ip][0] < now - window_seconds:
            self.requests[ip].popleft()
        
        # Check if already redirected recently (24 hour cooldown)
        if ip in self.redirected_ips and now - self.redirected_ips[ip] < 86400:  # 24 hours
            return True
        
        # Check rate limit
        if len(self.requests[ip]) >= max_requests:
            return True
        
        # Add current request
        self.requests[ip].append(now)
        return False
    
    def mark_redirected(self, ip):
        """Mark an IP as redirected to prevent repeated redirects"""
        self.redirected_ips[ip] = time.time()

# Global rate limiter instance
rate_limiter = RateLimiter()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_timeout": 20,
    "pool_size": 10,
    "max_overflow": 20,
    "connect_args": {
        "connect_timeout": 10,
        "application_name": "sliding_window_app"
    }
}

# Initialize database
db.init_app(app)

# Create all tables
with app.app_context():
    # Import models here to ensure they are registered
    from models import Review
    db.create_all()

def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

def get_client_ip():
    """Get the client's real IP address"""
    # Check for IP from reverse proxy headers
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for and isinstance(forwarded_for, str):
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip and isinstance(real_ip, str):
        return real_ip
    
    return request.remote_addr or '127.0.0.1'

def is_russian_ip(ip_address):
    """Check if IP address is from Russian IP ranges using known allocations"""
    try:
        ip = ipaddress.ip_address(ip_address)
        
        # Major Russian IP ranges (CIDR blocks allocated to Russia)
        russian_ranges = [
            '5.8.0.0/13',          # Rostelecom
            '5.16.0.0/13',         # Rostelecom
            '31.173.0.0/16',       # MTS
            '37.139.0.0/16',       # Beeline
            '46.17.0.0/16',        # Corbina Telecom
            '46.32.0.0/19',        # Petersburg Internet Network
            '77.88.0.0/18',        # Yandex
            '78.25.0.0/16',        # Rostelecom
            '78.108.0.0/16',       # TTK
            '81.176.0.0/13',       # Rostelecom
            '82.138.0.0/16',       # Corbina Telecom
            '85.21.0.0/16',        # Rostelecom
            '87.226.0.0/16',       # TTK
            '89.175.0.0/16',       # Petersburg Internet Network
            '91.103.0.0/16',       # Petersburg Internet Network
            '91.185.0.0/16',       # MTS
            '91.186.0.0/16',       # MTS
            '94.19.0.0/16',        # Petersburg Internet Network
            '95.24.0.0/16',        # Petersburg Internet Network
            '95.162.0.0/16',       # Petersburg Internet Network
            '176.59.0.0/16',       # Rostelecom
            '178.20.0.0/14',       # Rostelecom
            '178.176.0.0/12',      # Rostelecom
            '185.4.0.0/16',        # Selectel
            '188.113.0.0/16',      # Rostelecom
            '188.170.0.0/16',      # Rostelecom
            '212.1.0.0/16',        # Rostelecom
            '213.59.0.0/16'        # Rostelecom
        ]
        
        for cidr in russian_ranges:
            if ip in ipaddress.ip_network(cidr):
                return True
                
    except (ValueError, ipaddress.AddressValueError):
        pass
    
    return False

def check_geo_blocking():
    """Check if the request is from Russia and redirect if necessary"""
    try:
        client_ip = get_client_ip()
        
        # Validate IP address exists and is a string
        if not client_ip or not isinstance(client_ip, str):
            return None
        
        # Skip geo-blocking for localhost/development
        if client_ip in ['127.0.0.1', 'localhost', '::1'] or client_ip.startswith('192.168.'):
            return None
        
        # Skip for API endpoints to prevent context cancellation
        if request.path.startswith('/api/'):
            return None
        
        # Check rate limiting to prevent spam
        if rate_limiter.is_rate_limited(client_ip):
            # If rate limited, serve normal content instead of redirecting
            return None
            
        # Check if IP is from Russian ranges
        if is_russian_ip(client_ip):
            # Mark IP as redirected to prevent repeated redirects
            rate_limiter.mark_redirected(client_ip)
            
            # Log the redirect with rate limiting info
            logging.info(f"Redirecting Russian IP {client_ip} to Ukraine support (rate limited for 24h)")
            
            # Add cache headers to prevent excessive requests
            response = redirect('https://linktr.ee/UkraineTheLatest', code=301)  # Permanent redirect
            response.headers['Cache-Control'] = 'public, max-age=86400'  # 24 hour cache
            response.headers['Connection'] = 'close'  # Close connection cleanly
            return response
                
    except Exception as e:
        logging.warning(f"Geo-blocking error: {e}")
    
    return None

# Set up logging - use INFO level for production
log_level = logging.DEBUG if os.environ.get('FLASK_ENV') == 'development' else logging.INFO
logging.basicConfig(level=log_level)

# Apply security headers to all responses
app.after_request(add_security_headers)

# Apply geo-blocking check to all requests
@app.before_request
def before_request():
    """Check geo-blocking before processing any request"""
    redirect_response = check_geo_blocking()
    if redirect_response:
        return redirect_response

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
            window_str = ''.join(str(x) for x in window)
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
            window_str = ''.join(str(x) for x in window)
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
        
        # Helper function to format window size in code
        def get_java_code(template_name, k=window_size):
            java_templates = {
                'fixed_sum': f"""import java.util.*;

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
        int result = maxSumSubarray(arr, {k});
        System.out.println("Maximum sum of subarray of size {k}: " + result);
    }}
}}""",

                'fixed_max': f"""import java.util.*;

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
        List<Integer> result = maxInWindows(arr, {k});
        System.out.println("Maximum in each window of size {k}: " + result);
    }}
}}""",

                'fixed_min': f"""import java.util.*;

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
        List<Integer> result = minInWindows(arr, {k});
        System.out.println("Minimum in each window of size {k}: " + result);
    }}
}}""",

                'fixed_avg': f"""import java.util.*;

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
        List<Double> result = averageInWindows(arr, {k});
        System.out.println("Average of each window of size {k}: " + result);
    }}
}}""",

                'variable_longest_substring': """import java.util.*;

public class LongestSubstring {
    public static int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> charMap = new HashMap<>();
        int left = 0;
        int maxLength = 0;
        
        for (int right = 0; right < s.length(); right++) {
            char currentChar = s.charAt(right);
            
            if (charMap.containsKey(currentChar) && charMap.get(currentChar) >= left) {
                left = charMap.get(currentChar) + 1;
            }
            
            charMap.put(currentChar, right);
            maxLength = Math.max(maxLength, right - left + 1);
        }
        
        return maxLength;
    }
    
    public static void main(String[] args) {
        String s = "abcabcbb";
        int result = lengthOfLongestSubstring(s);
        System.out.println("Length of longest substring without repeating characters: " + result);
    }
}""",

                'variable_permutation_in_string': """import java.util.*;

public class PermutationInString {
    public static boolean checkInclusion(String s1, String s2) {
        if (s1.length() > s2.length()) {
            return false;
        }
        
        Map<Character, Integer> s1Count = new HashMap<>();
        for (char c : s1.toCharArray()) {
            s1Count.put(c, s1Count.getOrDefault(c, 0) + 1);
        }
        
        int windowSize = s1.length();
        for (int i = 0; i <= s2.length() - windowSize; i++) {
            String window = s2.substring(i, i + windowSize);
            Map<Character, Integer> windowCount = new HashMap<>();
            
            for (char c : window.toCharArray()) {
                windowCount.put(c, windowCount.getOrDefault(c, 0) + 1);
            }
            
            if (s1Count.equals(windowCount)) {
                return true;
            }
        }
        
        return false;
    }
    
    public static void main(String[] args) {
        String s1 = "ab";
        String s2 = "eidbaooo";
        boolean result = checkInclusion(s1, s2);
        System.out.println("Permutation of '" + s1 + "' exists in '" + s2 + "': " + result);
    }
}"""
            }
            return java_templates.get(template_name, "")
        
        # Generate code based on language and algorithm
        if language == 'java':
            if window_type == 'fixed':
                if algorithm == 'sum':
                    code = get_java_code('fixed_sum')
                elif algorithm == 'max':
                    code = get_java_code('fixed_max')
                elif algorithm == 'min':
                    code = get_java_code('fixed_min')
                elif algorithm == 'avg':
                    code = get_java_code('fixed_avg')
                else:
                    code = get_java_code('fixed_sum')  # Default
            else:  # variable window
                if algorithm == 'longest_substring':
                    code = get_java_code('variable_longest_substring')
                elif algorithm == 'permutation_in_string':
                    code = get_java_code('variable_permutation_in_string')
                else:
                    code = get_java_code('variable_longest_substring')  # Default
        
        elif language == 'python':
            code_templates = {
                'fixed': {
                    'sum': f'''def sliding_window_sum(arr, k={window_size}):
    """Find maximum sum of subarray of size k"""
    if len(arr) < k:
        return None
    
    # Calculate sum of first window
    window_sum = sum(arr[:k])
    max_sum = window_sum
    
    # Slide the window
    for i in range(k, len(arr)):
        # Remove first element of previous window and add current element
        window_sum = window_sum - arr[i - k] + arr[i]
        max_sum = max(max_sum, window_sum)
    
    return max_sum

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
result = sliding_window_sum(arr, {window_size})
print(f"Maximum sum of subarray of size {window_size}: {{result}}")''',
                    
                    'max': f'''def sliding_window_maximum(arr, k={window_size}):
    """Find maximum in each window of size k"""
    if len(arr) < k:
        return []
    
    from collections import deque
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
    """Find minimum in each window of size k"""
    if len(arr) < k:
        return []
    
    from collections import deque
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
    """Find average of each window of size k"""
    if len(arr) < k:
        return []
    
    result = []
    window_sum = sum(arr[:k])
    result.append(window_sum / k)
    
    for i in range(k, len(arr)):
        window_sum = window_sum - arr[i - k] + arr[i]
        result.append(window_sum / k)
    
    return result

# Example usage:
arr = [1, 2, 3, 4, 5, 6, 7, 8]
result = sliding_window_average(arr, {window_size})
print(f"Average of each window of size {window_size}: {{result}}")'''
                },
                'variable': {
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
                    
                    'permutation_in_string': '''def check_inclusion(s1, s2):
    """Check if any permutation of s1 exists in s2"""
    if len(s1) > len(s2):
        return False
    
    from collections import Counter
    
    s1_count = Counter(s1)
    window_size = len(s1)
    
    for i in range(len(s2) - window_size + 1):
        window = s2[i:i + window_size]
        window_count = Counter(window)
        
        if s1_count == window_count:
            return True
    
    return False

# Example usage:
s1 = "ab"
s2 = "eidbaooo"
result = check_inclusion(s1, s2)
print(f"Permutation of '{s1}' exists in '{s2}': {result}")'''
                }
            }
            code = code_templates.get(window_type, {}).get(algorithm, "# Python implementation for other algorithms not shown for brevity")
        
        elif language == 'java':
            if window_type == 'fixed':
                if algorithm == 'sum':
                    code = f'''import java.util.*;

public class SlidingWindowSum {{
    public static int slidingWindowSum(int[] arr, int k) {{
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
            windowSum = windowSum - arr[i - k] + arr[i];
            maxSum = Math.max(maxSum, windowSum);
        }}
        
        return maxSum;
    }}
    
    public static void main(String[] args) {{
        int[] arr = {{1, 2, 3, 4, 5, 6, 7, 8}};
        int result = slidingWindowSum(arr, {window_size});
        System.out.println("Maximum sum of subarray of size {window_size}: " + result);
    }}
}}'''
                else:
                    code = "// Java implementation for other algorithms not shown for brevity"
            else:  # variable window
                if algorithm == 'longest_substring':
                    code = '''import java.util.*;

public class LongestSubstring {
    public static int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> charMap = new HashMap<>();
        int left = 0;
        int maxLength = 0;
        
        for (int right = 0; right < s.length(); right++) {
            if (charMap.containsKey(s.charAt(right)) && charMap.get(s.charAt(right)) >= left) {
                left = charMap.get(s.charAt(right)) + 1;
            }
            
            charMap.put(s.charAt(right), right);
            maxLength = Math.max(maxLength, right - left + 1);
        }
        
        return maxLength;
    }
    
    public static void main(String[] args) {
        String s = "abcabcbb";
        int result = lengthOfLongestSubstring(s);
        System.out.println("Length of longest substring without repeating characters: " + result);
    }
}'''
                elif algorithm == 'permutation_in_string':
                    code = '''import java.util.*;

public class PermutationInString {
    public static boolean checkInclusion(String s1, String s2) {
        if (s1.length() > s2.length()) {
            return false;
        }
        
        Map<Character, Integer> s1Count = new HashMap<>();
        for (char c : s1.toCharArray()) {
            s1Count.put(c, s1Count.getOrDefault(c, 0) + 1);
        }
        
        int windowSize = s1.length();
        for (int i = 0; i <= s2.length() - windowSize; i++) {
            String window = s2.substring(i, i + windowSize);
            Map<Character, Integer> windowCount = new HashMap<>();
            
            for (char c : window.toCharArray()) {
                windowCount.put(c, windowCount.getOrDefault(c, 0) + 1);
            }
            
            if (s1Count.equals(windowCount)) {
                return true;
            }
        }
        
        return false;
    }
    
    public static void main(String[] args) {
        String s1 = "ab";
        String s2 = "eidbaooo";
        boolean result = checkInclusion(s1, s2);
        System.out.println("Permutation of '" + s1 + "' exists in '" + s2 + "': " + result);
    }
}'''
                else:
                    code = "// Java implementation for other variable window algorithms not shown for brevity"
        
        elif language == 'javascript':
            if window_type == 'fixed':
                if algorithm == 'sum':
                    code = f'''function slidingWindowSum(arr, k = {window_size}) {{
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
        windowSum = windowSum - arr[i - k] + arr[i];
        maxSum = Math.max(maxSum, windowSum);
    }}
    
    return maxSum;
}}

// Example usage:
const arr = [1, 2, 3, 4, 5, 6, 7, 8];
const result = slidingWindowSum(arr, {window_size});
console.log(`Maximum sum of subarray of size {window_size}: ${{result}}`);'''
                elif algorithm == 'max':
                    code = f'''function slidingWindowMaximum(arr, k = {window_size}) {{
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
console.log(`Maximum in each window of size {window_size}: ${{result}}`);'''
                elif algorithm == 'min':
                    code = f'''function slidingWindowMinimum(arr, k = {window_size}) {{
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
console.log(`Minimum in each window of size {window_size}: ${{result}}`);'''
                elif algorithm == 'avg':
                    code = f'''function slidingWindowAverage(arr, k = {window_size}) {{
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
console.log(`Average of each window of size {window_size}: ${{result}}`);'''
                else:
                    code = "// JavaScript implementation for other fixed window algorithms not shown for brevity"
            else:  # variable window
                if algorithm == 'longest_substring':
                    code = '''function longestSubstringWithoutRepeating(s) {
    const charMap = new Map();
    let left = 0;
    let maxLength = 0;
    
    for (let right = 0; right < s.length; right++) {
        if (charMap.has(s[right]) && charMap.get(s[right]) >= left) {
            left = charMap.get(s[right]) + 1;
        }
        
        charMap.set(s[right], right);
        maxLength = Math.max(maxLength, right - left + 1);
    }
    
    return maxLength;
}

// Example usage:
const s = "abcabcbb";
const result = longestSubstringWithoutRepeating(s);
console.log(`Length of longest substring without repeating characters: ${result}`);'''
                elif algorithm == 'permutation_in_string':
                    code = '''function checkInclusion(s1, s2) {
    if (s1.length > s2.length) {
        return false;
    }
    
    // Count characters in s1
    const s1Count = {};
    for (let char of s1) {
        s1Count[char] = (s1Count[char] || 0) + 1;
    }
    
    const windowSize = s1.length;
    for (let i = 0; i <= s2.length - windowSize; i++) {
        const window = s2.substring(i, i + windowSize);
        const windowCount = {};
        
        for (let char of window) {
            windowCount[char] = (windowCount[char] || 0) + 1;
        }
        
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
                else:
                    code = "// JavaScript implementation for other variable window algorithms not shown for brevity"
        
        elif language == 'cpp':
            if window_type == 'fixed':
                if algorithm == 'sum':
                    code = f'''#include <iostream>
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
}}'''
                else:
                    code = "// C++ implementation for other algorithms not shown for brevity"
            else:
                code = "// C++ implementation for variable window algorithms not shown for brevity"
        
        else:
            code = "# Language not supported"
        
        return jsonify({'code': code, 'language': language})
        
    except Exception as e:
        app.logger.error(f"Error generating code: {str(e)}")
        return jsonify({'error': 'An error occurred while generating code'})

@app.route('/api/reviews/submit', methods=['POST'])
def submit_review():
    try:
        data = request.get_json()
        
        if not data or 'rating' not in data:
            return jsonify({'error': 'Rating is required'}), 400
        
        rating = int(data['rating'])
        feedback = data.get('feedback', '').strip()
        
        if rating < 0 or rating > 5:
            return jsonify({'error': 'Rating must be between 0 and 5'}), 400
        
        if len(feedback) > 1000:
            return jsonify({'error': 'Feedback must be 1000 characters or less'}), 400
        
        # Get client IP
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        # Anti-spam: Check if this IP has submitted recently (24 hour cooldown)
        existing_review = Review.query.filter_by(ip_address=client_ip).order_by(Review.created_at.desc()).first()
        if existing_review:
            import datetime
            time_diff = datetime.datetime.utcnow() - existing_review.created_at
            if time_diff.total_seconds() < 86400:  # 24 hours
                return jsonify({'error': 'Please wait 24 hours before submitting another review'}), 429
        
        # Create new review
        review = Review(
            rating=rating,
            feedback=feedback if feedback else None,
            ip_address=client_ip
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Review submitted successfully!'})
        
    except ValueError:
        return jsonify({'error': 'Invalid rating value'}), 400
    except Exception as e:
        app.logger.error(f"Error submitting review: {str(e)}")
        return jsonify({'error': 'An error occurred while submitting your review'}), 500

@app.route('/api/reviews/stats')
def get_review_stats():
    try:
        # Get basic statistics
        total_reviews = Review.query.count()
        if total_reviews == 0:
            return jsonify({
                'total_reviews': 0,
                'average_rating': 0,
                'rating_distribution': {}
            })
        
        # Calculate average rating
        ratings = db.session.query(Review.rating).all()
        average_rating = sum(r[0] for r in ratings) / len(ratings)
        
        # Get rating distribution
        from collections import Counter
        rating_counts = Counter(r[0] for r in ratings)
        rating_distribution = {str(i): rating_counts.get(i, 0) for i in range(0, 6)}
        
        return jsonify({
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 1),
            'rating_distribution': rating_distribution
        })
        
    except Exception as e:
        app.logger.error(f"Error getting review stats: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching review statistics'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)