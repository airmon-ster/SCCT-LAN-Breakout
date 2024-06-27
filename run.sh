#!/bin/bash
curr_dir=$(pwd -P) 
echo "$curr_dir"
# Check for Python installation

if python3 --version &> /dev/null; then
    echo "Python3 is installed."
    py_version='python3'
elif python --version &> /dev/null; then
    echo "Python is installed."
    py_version='python'
else
    echo "Python is not installed. Please install Python before continuing."
    exit 1
fi


# # Launch default web browser with specified parameters
# echo "Launching default web browser..."
# # Check if OS is macOS or Linux and open Chrome accordingly
# if [[ $(uname) == "Darwin" ]]; then
#     open -na "Google Chrome" --args --disable-pinch --guest --disable-extensions --app="http://127.0.0.1:8000"
# elif [[ $(uname) == "Linux" ]]; then
#     google-chrome --disable-pinch --guest --disable-extensions --app="http://127.0.0.1:8000"
# else
#     echo "Unsupported operating system."
#     exit 1
# fi

# Install Python Dependencies and Run Python script gui.py
echo "Checking Python dependencies..."
$py_version -m pip install -r "$curr_dir/requirements.txt"
echo "Running Python script gui.py..."
$py_version "$curr_dir/gui.py"
