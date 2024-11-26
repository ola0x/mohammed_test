# Technical Test Assignment: Service Startup Script

## Overview
Create a bash script that automates the startup sequence for a retail monitoring system. The script should handle NGROK tunneling and multiple Python applications in a specific order.

## Task Description
You need to create a single bash script that manages the startup of three services:
1. NGROK tunnel
2. Main application script
3. Dashboard script

## Technical Requirements

### NGROK Configuration
- Command to execute: `ngrok http --domain=man-trusting-eanly.ngrok.app 5000`
- Must start before other services

### Python Environment
- Virtual environment location: `C:\Users\USER\Desktop\RetailUlimited\yolo\antitheft\mohammed_t`
- Must be activated before running Python scripts

### Python Scripts
1. Main Application
   - Script: `app.py`
   - Location: Root of virtual environment directory

2. Dashboard Application
   - Script: `dash.py`
   - Location: Root of virtual environment directory

## Implementation Requirements

### Script Behavior
- All services must run concurrently (in background)
- Services must start in the specified order:
  1. NGROK
  2. Main application (app.py)
  3. Dashboard (dash.py)
- The script should handle errors appropriately

### Documentation
Provide instructions that include:
- How to run the script
- Prerequisites
- Troubleshooting steps
- How to stop the services

## Submission Guidelines
Submit:
1. The bash script
2. Documentation for running the script

## Evaluation Criteria
Your solution will be evaluated on:
- Functionality (40%)
  - Correct service startup sequence
  - Proper environment activation
  - Background process management
- Documentation (60%)
  - Clear instructions
  - Complete prerequisites
  - Troubleshooting guidance

## Time Allocation
- Total time: 1 hour
- Recommended breakdown:
  - Planning: 10 minutes
  - Implementation: 30 minutes
  - Testing: 10 minutes
  - Documentation: 10 minutes

## Testing Environment
- The script must work on Windows systems
- Test with provided paths
- Verify all services start correctly

## Support
If you have questions about the requirements, please ask before starting the implementation.

---
Good luck with your implementation!
