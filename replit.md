# Sliding Window Technique Visualizer

## Overview

This is an interactive educational web application designed to teach sliding window algorithms through dynamic visualizations. The application provides a comprehensive learning platform with real-time animations, multi-language code generation, and step-by-step algorithm analysis.

## System Architecture

### Frontend Architecture
- **Framework**: Vanilla JavaScript with Bootstrap 5 for UI components
- **Styling**: Custom CSS with Bootstrap dark theme integration
- **Visualization Engine**: Custom JavaScript class `SlidingWindowVisualizer` for real-time algorithm demonstration
- **Responsive Design**: Mobile-first approach using Bootstrap's grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **API Design**: RESTful endpoints for input validation and algorithm calculations
- **Session Management**: Flask sessions with configurable secret key
- **Error Handling**: Comprehensive exception handling with logging

### Core Components
1. **Visualization Engine** (`SlidingWindowVisualizer` class):
   - Manages array/string visualization with animated sliding windows
   - Handles both fixed and variable window size algorithms
   - Provides real-time animation controls (play/pause/speed adjustment)
   - Generates comprehensive analysis summaries

2. **Algorithm Implementations**:
   - Fixed Window: Sum, Maximum, Minimum, Average calculations
   - Variable Window: Longest substring without repeating characters, Pattern matching
   - Multi-language code generation (Python, Java, JavaScript, C++)

3. **API Endpoints**:
   - `/api/validate_input`: Input validation for arrays and strings
   - `/api/calculate_step`: Step-by-step algorithm calculations

## Key Components

### Frontend Components
- **Interactive Visualization Panel**: Real-time sliding window animation with color-coded elements
- **Algorithm Configuration**: Dynamic form controls for window type and algorithm selection
- **Analysis Dashboard**: Comprehensive results table with step-by-step breakdown
- **Code Generator**: Multi-language implementation with copy/download functionality
- **Control Panel**: Play/pause controls with adjustable animation speed
- **Language Support**: Automatic browser locale detection with English/Spanish support

### Backend Components
- **Input Validator**: Robust validation for array and string inputs with error handling
- **Algorithm Calculator**: Core sliding window logic implementation
- **Template Renderer**: Flask template system for dynamic HTML generation

## Data Flow

1. **User Input**: User selects algorithm type and enters data through web interface
2. **Client-Side Validation**: JavaScript performs initial input validation and formatting
3. **Server-Side Validation**: Flask API validates and parses input data
4. **Algorithm Execution**: Server calculates algorithm steps and returns structured data
5. **Visualization Update**: Client receives data and updates visualization with animations
6. **Analysis Generation**: System generates comprehensive analysis tables and code examples

## External Dependencies

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Bootstrap Icons**: Icon library for consistent visual elements
- **Replit Bootstrap Theme**: Custom dark theme integration

### Backend Dependencies
- **Flask**: Core web framework for Python backend
- **Python Standard Library**: Logging, OS environment handling

### Development Dependencies
- **pytest**: Python testing framework
- **Node.js**: JavaScript testing environment

## Deployment Strategy

### Platform Configuration
- **Target Platform**: Replit hosting environment
- **Entry Point**: `main.py` imports Flask app from `app.py`
- **Static Assets**: Served through Flask's static file handling
- **Environment Variables**: Session secret configuration through environment variables

### Testing Strategy
- **Backend Testing**: 23 comprehensive pytest unit tests covering API endpoints and core functionality
- **Frontend Testing**: 14 JavaScript unit tests validating visualization logic
- **Test Coverage**: 100% pass rate with comprehensive error scenario coverage
- **Test Runner**: Custom `run_tests.py` script for unified test execution

### Production Considerations
- Configurable session secrets for security
- Comprehensive error logging and debugging support
- Responsive design for cross-device compatibility
- Performance optimized animations with configurable speed controls

## Changelog

```
Changelog:
- July 01, 2025: Initial setup
- July 01, 2025: Added comprehensive Spanish language support with automatic browser locale detection
- July 01, 2025: Completed full Spanish translation system including:
  * Fixed hardcoded START/END labels (now INICIO/FIN in Spanish)
  * Translated all calculation descriptions (Sum of window → Suma de ventana)
  * Implemented JavaScript-based translatable window labels
  * Fixed all remaining English text in Spanish mode
  * Ready for deployment with complete bilingual support
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```