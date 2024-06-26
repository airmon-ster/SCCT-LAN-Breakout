#!/bin/bash
# Check for Python installation
if python3 --version &> /dev/null; then
    echo "Python3 is installed."
else
    echo "Python3 is not installed. Please install Python before continuing."
    exit 1
fi

# Launch default web browser with specified parameters
echo "Launching default web browser..."
open -a "Google Chrome" --args --disable-pinch --guest --disable-extensions --app=http://127.0.0.1:8000
# For Linux, you might want to change `open -a "Google Chrome"` to `google-chrome` or another browser depending on what's installed

# Install Python Dependencies and Run Python script gui.py
echo "Checking Python dependencies..."
python3 -m pip install -r requirements.txt
echo "Running Python script gui.py..."
python3 gui.py
