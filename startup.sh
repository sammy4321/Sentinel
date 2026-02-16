#!/bin/bash
set -e

# Configuration
PYTHON_VERSION="3.11"
PYTHON_CMD="python$PYTHON_VERSION"
VENV_DIR=".venv"

# Check for Python version
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "$PYTHON_CMD could not be found."
    
    if command -v brew &> /dev/null; then
        echo "Attempting to install $PYTHON_CMD via Homebrew..."
        brew install python@$PYTHON_VERSION
    else
        echo "Error: $PYTHON_CMD is required but not found."
        echo "Homebrew is also not found, so we cannot auto-install it."
        echo "Please install Python $PYTHON_VERSION manually and try again."
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv $VENV_DIR
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

echo "Starting application..."
python main.py "$@"
