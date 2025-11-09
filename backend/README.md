# AI Knowledge Engine Backend

FastAPI backend for AI-powered ticket analysis and resolution system.

## Features

- **Ticket Analysis API**: Analyze support tickets for priority, category, and sentiment
- **Embedding Generation**: Use SentenceTransformer to generate text embeddings
- **Priority Detection**: Keyword-based priority classification (High/Medium/Low)
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **CORS Support**: Configured for React frontend integration
- **File Upload**: Support for text file uploads (.txt, .json, .csv)

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **PostgreSQL**: Reliable database
- **SQLAlchemy**: Python SQL toolkit and ORM
- **SentenceTransformer**: Text embedding generation
- **Uvicorn**: ASGI server

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip or conda package manager

## Installation

1. **Clone and navigate to backend directory**:
   ```bash
   cd ai-knowledge-engine/backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**:
   ```bash
   # Create database
   createdb support_tickets_db
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE support_tickets_db;
   \q
   ```

5. **Configure environment variables** (optional):
   ```bash
   # Create .env file
   echo "DATABASE_URL=postgresql://postgres:password@localhost/support_tickets_db" > .env
   ```

## Running the Application

### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
- **GET** `/` - Root endpoint with basic info
- **GET** `/health` - Health check endpoint

### Ticket Analysis
- **POST** `/api/analyze_ticket` - Analyze ticket text
- **POST** `/api/analyze_ticket_file` - Analyze uploaded file
- **GET** `/api/health` - Service health check

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### Analyze Ticket Text

```bash
curl -X POST "http://localhost:8000/api/analyze_ticket" \
     -H "Content-Type: application/json" \
     -d '{
       "ticket_text": "I am getting an error when trying to login. The system crashed and is not working. This is urgent!",
       "file_name": null
     }'
```

### Analyze Uploaded File

```bash
curl -X POST "http://localhost:8000/api/analyze_ticket_file" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@ticket.txt"
```

## Response Format

```json
{
  "priority": "High",
  "category": "Technical Issue",
  "sentiment": "negative",
  "confidence": 0.85,
  "embedding_preview": [0.1, -0.2, 0.3, -0.4, 0.5],
  "detected_keywords": ["error", "crash", "urgent"],
  "suggested_articles": [
    "How to resolve technical issue",
    "Common high priority issues",
    "General troubleshooting guide"
  ],
  "processing_time_ms": 245.67,
  "model_info": {
    "model_name": "all-MiniLM-L6-v2",
    "model_loaded": true,
    "max_seq_length": 256,
    "embedding_dimension": 384
  }
}
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level (default: INFO)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Database Schema

The application automatically creates the following tables:
- `ticket_analyses`: Stores analysis results
- `support_tickets`: Stores support ticket data
- `knowledge_articles`: Stores knowledge base articles
- `analysis_logs`: Stores API request/response logs

## Development

### Code Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── routes/            # API route definitions
│   │   └── ticket_routes.py
│   ├── services/          # Business logic services
│   │   └── embedding_service.py
│   ├── db/               # Database configuration
│   │   ├── database.py
│   │   └── schemas.py
│   └── utils/            # Utility functions
│       └── text_cleaner.py
```

### Adding New Features

1. **New API endpoints**: Add to `app/routes/`
2. **New services**: Add to `app/services/`
3. **New database models**: Add to `app/db/schemas.py`
4. **New utilities**: Add to `app/utils/`

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_ticket_routes.py
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure PostgreSQL is running
   - Check database credentials
   - Verify database exists

2. **Model Loading Error**:
   - Check internet connection (first run downloads model)
   - Ensure sufficient disk space
   - Check Python version compatibility

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

### Logs

Check application logs for detailed error information:
```bash
# Run with verbose logging
uvicorn main:app --reload --log-level debug
```

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
