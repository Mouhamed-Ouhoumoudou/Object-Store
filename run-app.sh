#!/usr/bin/env bash

# Load venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
fastapi dev app/main.py

