@echo off
REM Start the Map Dater API backend server

echo Starting Map Dater API Backend...
echo.
echo Make sure you have installed dependencies:
echo   pip install -r requirements.txt
echo.
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.

REM Start the server
python api_server.py
