#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing requirements..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Precompute all journey data
echo "Precomputing journey data..."
python3 -c "from app.utils.cache import journey_cache; journey_cache.precompute_all_journeys()"

# Start the Flask application
echo "Starting PathPilot..."
python run.py 