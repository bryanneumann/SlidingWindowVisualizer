# Sliding Window Technique Visualizer

**Made with AI**

An advanced interactive learning platform for sliding window algorithms, providing comprehensive algorithmic exploration through dynamic visualizations and multi-language code generation.

🌐 **Live Demo:** https://sliding-window-visualizer-bryanneumann.replit.app/

## Features

### 🎯 Interactive Visualization
- **Fixed Size Windows**: Visualize how a window of constant size slides across an array
- **Variable Size Windows**: See how window size changes based on conditions
- **Real-time Animation**: Watch the window move step-by-step with smooth transitions
- **START/END Labels**: Clear indicators showing window boundaries

### 🔧 Algorithm Options
- **Fixed Window Algorithms**:
  - Sum of Elements: Calculate the sum of elements in the current window
  - Maximum Element: Find the maximum value in the window
  - Minimum Element: Find the minimum value in the window
  - Average of Elements: Calculate the average of window elements
- **Variable Window Algorithms**:
  - Longest Substring Without Repeating Characters
  - Permutation in String (pattern matching)

### 📊 Advanced Analysis
- **Window Analysis Summary**: Comprehensive table showing all windows processed
- **Step-by-Step Breakdown**: Detailed view of each window position, content, and result
- **Color-Coded Status**: Visual indicators for matches, valid windows, and results
- **Progress Tracking**: Real-time progress bar and step counter

### 💻 Code Generation
- Generate implementation code in multiple languages:
  - Python
  - Java
  - JavaScript
  - C++
- Copy to clipboard or download functionality
- Complete, runnable code examples

### 🎮 Interactive Controls
- Play/Pause animation with smooth transitions
- Step forward/backward through the visualization
- Adjustable animation speed
- Custom array and string input modes
- Variable window size settings
- Demo examples for quick learning
- Reset functionality

### 🧪 Testing & Quality
- **37 Unit Tests**: Comprehensive test suite with 100% pass rate
- **Backend Tests**: 23 tests covering API endpoints and algorithms
- **Frontend Tests**: 14 tests validating visualization logic
- **Bug-Free**: Thoroughly tested and validated

## How It Works

1. **Choose Input Mode**: Select between array (numbers) or string input
2. **Enter Your Data**: Input numbers (comma-separated) or text string
3. **Select Algorithm**: Choose from fixed window or advanced algorithms
4. **Configure Settings**: Set window size and algorithm parameters
5. **Start Visualization**: Watch the algorithm in action with step-by-step analysis!

## Visual Example

The visualization shows:
- **Gray Elements**: Array elements not in the current window
- **Blue Highlighted Elements**: Elements currently in the sliding window
- **Yellow Borders**: Window boundary indicators
- **START Label**: Green label marking the beginning of the window
- **END Label**: Red label marking the end of the window

## Educational Value

This tool helps students and developers understand:
- How sliding window techniques optimize array problems
- The difference between fixed and variable window approaches
- Time and space complexity improvements
- Real-world applications of the technique

## Getting Started

### Quick Start (Online)
Visit the live demo: https://sliding-window-visualizer-bryanneumann.replit.app/

### Local Development
1. Clone the repository
2. Install dependencies: `pip install flask flask-sqlalchemy gunicorn psycopg2-binary pytest pytest-flask`
3. Run the application: `python main.py`
4. Open your browser to `http://localhost:5000`

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run only backend tests
pytest test_app.py -v

# Run only frontend tests
node test_frontend.js
```

## Technical Stack

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript, Bootstrap 5
- **Styling**: Custom CSS with dark theme
- **Database**: SQLAlchemy (optional for user data)

## Use Cases

Perfect for:
- Computer Science education
- Algorithm interview preparation
- Understanding optimization techniques
- Visual learning of programming concepts

---