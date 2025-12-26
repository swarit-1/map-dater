#!/bin/bash
# Start the Map Dater API backend server

echo "============================================================"
echo "Starting Map Dater API Backend..."
echo "============================================================"
echo ""
echo "Make sure you have installed dependencies:"
echo "  pip install -r requirements.txt"
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Features available:"
echo "  - Map Analysis (Image to Date): POST /analyze"
echo "  - Map Generation (Date to Image): POST /generate"
echo "  - Game Mode: POST /game/start"
echo ""

# Start the server
python api_server.py
