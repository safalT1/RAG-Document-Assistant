#!/bin/bash

echo "Starting RAG Document Assistant..."

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the FastAPI app
echo "Starting the API server on http://127.0.0.1:8000"
uvicorn app.main:app --reload
