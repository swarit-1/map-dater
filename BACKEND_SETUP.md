# Backend API Setup Guide

This guide explains how to run the Map Dater backend API server.

## Prerequisites

- Python 3.8 or higher
- All dependencies from `requirements.txt`
- Tesseract OCR installed (for text extraction)

## Installation

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- python-multipart (for file uploads)
- All other Map Dater dependencies

2. **Verify Tesseract is installed:**

```bash
tesseract --version
```

If not installed, see [ENV_SETUP.md](ENV_SETUP.md) for installation instructions.

## Starting the Backend

### Option 1: Quick Start (Recommended)

**Windows:**
```bash
start_backend.bat
```

**Linux/Mac:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

### Option 2: Direct Python

```bash
python api_server.py
```

### Option 3: Uvicorn with Auto-reload (Development)

```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag automatically restarts the server when code changes.

## Verifying the Backend

Once started, the backend will be available at:
- **API Base URL:** http://localhost:8000
- **Interactive API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

Test the health endpoint:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "online",
  "service": "Map Dater API",
  "version": "1.0.0"
}
```

## API Endpoints

### 1. Health Check
- **Endpoint:** `GET /`
- **Description:** Verify the API is running
- **Response:** Status information

### 2. Analyze Map
- **Endpoint:** `POST /analyze`
- **Description:** Upload and analyze a historical map
- **Content-Type:** `multipart/form-data`
- **Request Body:**
  - `file`: Image file (JPG, PNG, etc.)
- **Response:**
  ```json
  {
    "date_range": [1949, 1990],
    "most_likely_year": 1970,
    "confidence": 0.87,
    "evidence": [
      {
        "label": "East Germany",
        "valid_range": [1949, 1990],
        "explanation": "GDR existed 1949-1990..."
      }
    ]
  }
  ```

### 3. Start Game Round
- **Endpoint:** `POST /game/start?difficulty=beginner`
- **Description:** Start a new game round
- **Query Parameters:**
  - `difficulty`: `beginner`, `intermediate`, or `expert`
- **Response:**
  ```json
  {
    "round_id": "abc123",
    "map_description": "Cold War era map...",
    "difficulty": "beginner"
  }
  ```

### 4. Submit Guess
- **Endpoint:** `POST /game/submit`
- **Description:** Submit a guess for a game round
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "round_id": "abc123",
    "guess": 1970  // or [1960, 1980] for range
  }
  ```
- **Response:**
  ```json
  {
    "score": 85,
    "was_accurate": true,
    "feedback": ["Excellent!", "You identified..."],
    "system_estimate": {
      "range": [1949, 1990],
      "most_likely": 1970
    }
  }
  ```

## Testing the API

### Using the Interactive Docs

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

### Using curl

**Analyze a map:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@path/to/your/map.jpg"
```

**Start a game:**
```bash
curl -X POST "http://localhost:8000/game/start?difficulty=beginner"
```

**Submit a guess:**
```bash
curl -X POST http://localhost:8000/game/submit \
  -H "Content-Type: application/json" \
  -d '{"round_id": "abc123", "guess": 1970}'
```

## Connecting the Frontend

The frontend is already configured to connect to `http://localhost:8000` by default.

To start both backend and frontend:

1. **Terminal 1 - Backend:**
   ```bash
   python api_server.py
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

Then open http://localhost:5173 in your browser.

## Configuration

### Changing the API Port

Edit `api_server.py` at the bottom:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
```

### Changing CORS Settings

Edit the CORS middleware in `api_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend API URL

If you change the backend port, update the frontend:

Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

Or edit `frontend/src/api/mapDaterApi.ts`:
```typescript
const API_BASE_URL = 'http://localhost:YOUR_PORT';
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac - Find and kill process
lsof -ti:8000 | xargs kill -9
```

Or change the port in `api_server.py`.

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### CORS Errors

If you see CORS errors in the browser console:
1. Check the frontend URL is in the `allow_origins` list
2. Make sure both backend and frontend are running
3. Try clearing browser cache

### Tesseract Not Found

If you get "Tesseract not found" errors:
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Mac: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

Then verify:
```bash
tesseract --version
```

## Production Deployment

For production deployment, use a production-grade ASGI server:

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Or deploy to platforms like:
- **Render**: Connect your GitHub repo, select `api_server.py`
- **Railway**: Deploy with `railway up`
- **Fly.io**: Use `fly launch`
- **AWS Lambda**: Use Mangum adapter
- **Docker**: See below

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "api_server.py"]
```

Build and run:
```bash
docker build -t map-dater-api .
docker run -p 8000:8000 map-dater-api
```

## Next Steps

- See [frontend/README.md](frontend/README.md) for frontend setup
- See [QUICKSTART.md](QUICKSTART.md) for full system overview
- Check [API documentation](http://localhost:8000/docs) when server is running
