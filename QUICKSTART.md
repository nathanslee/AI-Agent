# Quick Start Guide - AI Database Assistant

Get up and running in 5 minutes!

## TL;DR

```bash
# 1. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Then edit .env with your OpenAI API key
mkdir databases
uvicorn app.main:app --reload --port 8000

# 2. Frontend Setup (new terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev

# 3. Open browser
# http://localhost:3000
```

## What You Need

1. **OpenAI API Key** (Required)
   - Get it: https://platform.openai.com/api-keys
   - Cost: ~$0.01 per database creation

2. **Plaid API** (Optional - for banking features)
   - Get it: https://dashboard.plaid.com/signup
   - Free sandbox for testing

## Step-by-Step

### 1. Setup Backend (2 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```env
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET=random-secret-at-least-32-chars
PLAID_CLIENT_ID=optional
PLAID_SECRET=optional
PLAID_ENV=sandbox
```

Start backend:
```bash
mkdir databases
uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend (1 minute)

Open a NEW terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start frontend:
```bash
npm run dev
```

### 3. Test It! (2 minutes)

1. Open http://localhost:3000
2. Click "Sign Up" → Create account
3. Click "Create New Database"
4. Type: "Track grocery items with name, store, date, and expiration"
5. Click "Generate Database"
6. Add some items!

## Example Natural Language Commands

Once you have a database:

- "Add bananas bought today at Trader Joe's"
- "Show me all items expiring this week"
- "Add milk, expires in 7 days"
- "Show me everything I bought at Whole Foods"

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │  Next.js 14 + TailwindCSS
│   Port 3000     │  Premium UI, Dynamic Forms
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   Backend API   │  FastAPI + Python
│   Port 8000     │  REST API
└────────┬────────┘
         │
    ┌────┴─────┬──────────────┐
    ▼          ▼              ▼
┌────────┐  ┌──────┐    ┌──────────┐
│SQLite  │  │OpenAI│    │  Plaid   │
│Per-User│  │ GPT-4│    │(optional)│
└────────┘  └──────┘    └──────────┘
```

## Key Features

✅ **Natural Language Database Creation**
- Just describe what you want to track
- AI generates the perfect schema

✅ **Per-User Isolation**
- Each user gets their own databases
- Complete data privacy

✅ **Dynamic Forms**
- Forms auto-generate from schema
- No coding required

✅ **AI-Powered Queries**
- Natural language → SQL
- Smart suggestions

✅ **Banking Integration**
- Connect with Plaid
- Auto-sync transactions

✅ **Premium Design**
- Alex Bender-inspired aesthetic
- Glassmorphism effects
- Smooth animations

## Folder Structure

```
AI Agent/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI routes
│   │   ├── database.py       # Database manager
│   │   ├── auth.py           # JWT authentication
│   │   ├── ai_agent.py       # OpenAI integration
│   │   ├── sql_validator.py  # SQL safety
│   │   └── plaid_integration.py
│   ├── databases/            # User data storage
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    ├── app/
    │   ├── page.tsx          # Landing page
    │   ├── login/
    │   ├── signup/
    │   ├── dashboard/        # Database list
    │   ├── wizard/create/    # DB creation wizard
    │   └── database/[id]/    # Database detail view
    ├── components/
    │   ├── ui/               # shadcn/ui components
    │   └── Navigation.tsx
    ├── lib/
    │   ├── api.ts            # API client
    │   └── auth.ts           # Auth helpers
    └── .env.local
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Databases
- `GET /api/databases` - List user databases
- `POST /api/databases/create` - Create via natural language
- `GET /api/databases/{id}` - Get database details
- `DELETE /api/databases/{id}` - Delete database

### Data Operations
- `GET /api/data/{db_id}` - Get all data
- `POST /api/data/{db_id}/insert` - Insert data via form
- `POST /api/execute/natural` - Natural language command
- `POST /api/execute/sql` - Execute SQL (validated)

### AI Features
- `POST /api/ai/suggest-expiration` - Suggest expiration date
- `POST /api/ai/categorize` - Auto-categorize item
- `GET /api/ai/suggestions/{db_id}` - Get query suggestions

### Plaid
- `POST /api/plaid/create-link-token` - Create Plaid Link
- `POST /api/plaid/exchange-token` - Exchange public token
- `POST /api/plaid/sync-transactions` - Import transactions

## Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ SQL injection prevention
- ✅ User data isolation
- ✅ Destructive operation confirmations
- ✅ Input validation and sanitization

## Troubleshooting

**"ModuleNotFoundError"**
→ Activate virtual environment and install dependencies

**"OPENAI_API_KEY not found"**
→ Create `.env` file in backend folder

**"Failed to fetch"**
→ Make sure backend is running on port 8000

**"Database creation failed"**
→ Check OpenAI API key is valid and has credits

## Next Steps

1. ✅ Create your first database
2. ✅ Add some test data
3. ✅ Try natural language commands
4. ✅ Connect Plaid (optional)
5. ✅ Deploy to production (see DEPLOYMENT.md)

## Cost Estimates

**Development (testing):**
- ~$1-2 for 100 database creations
- ~$0.50 for 1000 natural language queries

**Production (per user per month):**
- ~$0.10-0.50 depending on usage
- Plaid is free for sandbox, $0.15/user/month for production

## Performance

- Database creation: ~2-3 seconds
- Natural language query: ~1-2 seconds
- Form submission: <100ms
- Table view load: <100ms

## Browser Support

- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

## Tech Stack Summary

**Frontend:**
- Next.js 14 (App Router)
- TailwindCSS
- shadcn/ui
- Framer Motion
- Axios

**Backend:**
- FastAPI
- OpenAI GPT-4
- SQLite
- Plaid
- Pydantic
- JWT

## Support

Need help?
1. Check DEPLOYMENT.md for detailed guide
2. Check backend logs: `uvicorn app.main:app --log-level debug`
3. Check browser console for frontend errors
4. Visit OpenAI docs: https://platform.openai.com/docs

Happy building! 🚀
