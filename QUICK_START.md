# Quick Start Guide

## Prerequisites Check ✅

- [x] PostgreSQL installed and running
- [x] Database `support_tickets` created
- [x] Python 3.11+ installed
- [x] Node.js 16+ installed
- [x] Backend `.env` file configured
- [x] All dependencies listed in requirements.txt

## Step 1: Start Backend

```bash
# Navigate to backend directory
cd ai-knowledge-engine/backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
- Server starting on http://0.0.0.0:8000
- Database tables created automatically
- Models loading in background
- API docs available at http://localhost:8000/docs

## Step 2: Start Frontend

Open a **new terminal** window:

```bash
# Navigate to frontend directory
cd ai-knowledge-engine/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected output:**
- Frontend running on http://localhost:5173
- Browser should open automatically

## Step 3: Test the Application

1. **Register a new account:**
   - Go to http://localhost:5173
   - Click "Sign Up"
   - Enter name, email, and password (min 6 characters)
   - Submit

2. **Login:**
   - Use your registered email and password
   - You should be redirected to the dashboard

3. **Test Ticket Analysis:**
   - Navigate to ticket analysis page
   - Enter or upload a support ticket
   - View AI-powered analysis results

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user (also available at `/api/auth/register` for backward compatibility)
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires Bearer token)

### Ticket Analysis
- `POST /api/analyze_ticket` - Analyze ticket text
- `POST /api/analyze_ticket_file` - Analyze uploaded file
- `POST /api/recommend` - Get article recommendations
- `GET /api/topics` - Get topic analysis
- `GET /api/usage` - Get usage statistics

### Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Backend Issues

**Database Connection Error:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env` file
- Verify database `support_tickets` exists

**Port Already in Use:**
- Change port: `uvicorn main:app --reload --port 8001`
- Update frontend `.env` if needed

**Module Not Found:**
- Activate virtual environment
- Run: `pip install -r requirements.txt`

### Frontend Issues

**Cannot Connect to Backend:**
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify `VITE_API_URL` in frontend `.env` (optional)

**npm install fails:**
- Clear cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:pass2004@localhost:5432/support_tickets
SECRET_KEY=your-secret-key-change-in-production
HUGGINGFACE_TOKEN=your_token_here (optional)
```

### Frontend (.env) - Optional
```
VITE_API_URL=http://localhost:8000
```

## Next Steps

1. ✅ Backend and Frontend are running
2. ✅ Authentication is working
3. ✅ Database tables are created
4. ✅ API endpoints are accessible
5. 🚀 Start using the application!

