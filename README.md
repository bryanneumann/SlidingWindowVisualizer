# Sliding Window Technique Visualizer

**Made with AI**

An interactive web application that demonstrates sliding window techniques for both fixed and variable size windows. Built with Flask and vanilla JavaScript to provide educational visualizations of this important programming technique.

Deployed to https://replit.com/@bryanneumann/SlidingWindowVisualizer

## Features

### 🎯 Interactive Visualization
- **Fixed Size Windows**: Visualize how a window of constant size slides across an array
- **Variable Size Windows**: See how window size changes based on conditions
- **Real-time Animation**: Watch the window move step-by-step with smooth transitions
- **START/END Labels**: Clear indicators showing window boundaries

### 🔧 Technique Options
- **Sum of Elements**: Calculate the sum of elements in the current window
- **Maximum Element**: Find the maximum value in the window
- **Minimum Element**: Find the minimum value in the window
- **Average of Elements**: Calculate the average of window elements

### 💻 Code Generation
- Generate implementation code in multiple languages:
  - Python
  - Java
  - JavaScript
  - C++
- Copy to clipboard or download functionality
- Complete, runnable code examples

### 🎮 Interactive Controls
- Play/Pause animation
- Step forward/backward through the visualization
- Adjustable animation speed
- Custom array input
- Variable window size settings

## How It Works

1. **Enter Your Data**: Input an array of numbers (comma-separated)
2. **Choose Technique**: Select the calculation method (sum, max, min, average)
3. **Set Window Type**: Choose between fixed or variable size windows
4. **Configure Window Size**: Set the size for fixed windows
5. **Start Visualization**: Watch the technique in action!

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

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Open your browser to `http://localhost:5000`

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