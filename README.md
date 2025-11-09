# AI Knowledge Engine

AI Knowledge Engine is a full-stack application that analyzes customer support tickets and surfaces actionable insights with AI-assisted recommendations. It consists of a FastAPI backend that powers the analysis pipeline and a React frontend for the operator dashboard.

## Project Structure

```
ai-knowledge-engine/
├── backend/           # FastAPI application and services
├── frontend/          # React dashboard (Vite + Tailwind)
└── README.md          # Project documentation
```

## Features

- Ticket prioritization and category detection
- SentenceTransformer embeddings with FAISS-based article recommendations
- Language detection and basic sentiment indicators
- BERTopic-driven topic insights and mock usage analytics
- React dashboard with ticket submission, analysis visualisation, and charts

## Prerequisites

- Python 3.11+
- Node.js 16+
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Vaishnavi4104/AI-Knowledge-Engine.git
cd AI-Knowledge-Engine
```

### 2. Back-end setup

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

# Run the API server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Optional: ensure `backend/data/knowledge_base.pkl` exists or populate the knowledge base before requesting recommendations.

### 3. Front-end setup

```bash
cd ../frontend
npm install
npm run dev
```

The frontend dev server runs on `http://localhost:5173` by default. Make sure the backend is running at `http://localhost:8000` (the default base URL in `frontend/src/api/axiosConfig.js`).

## Running Endpoint Tests

From the `backend` directory:

```bash
python test_endpoints.py
```

This script exercises the health, ticket analysis, recommendation, topics, and usage endpoints. The server must be running before executing the tests.

## Environment Variables

Create a `.env` file if you need to override defaults:

```
# backend/.env
DATABASE_URL=postgresql://user:password@localhost/support_tickets_db
LOG_LEVEL=INFO

# frontend/.env
VITE_API_URL=http://localhost:8000
```

## Contributing

1. Fork the repo and create a feature branch
2. Make your changes and add tests where applicable
3. Run linting/tests locally
4. Submit a pull request describing the change and validation steps

## License

This project is released under the MIT License. See the `LICENSE` file for details.
