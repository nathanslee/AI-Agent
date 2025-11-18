# AI Database Assistant

A premium full-stack AI-powered database assistant with per-user storage, natural language interfaces, and Plaid integration.

## Architecture

- **Frontend**: Next.js 14 (App Router) + TailwindCSS + shadcn/ui
- **Backend**: FastAPI + Python
- **Database**: SQLite (per-user isolated databases)
- **AI**: OpenAI GPT-4
- **Banking**: Plaid API

## Features

- ✅ User authentication with JWT
- ✅ Per-user isolated database storage
- ✅ Natural language database creation
- ✅ Dynamic UI form generation
- ✅ AI-powered SQL generation
- ✅ Plaid banking integration
- ✅ Smart suggestions (expiration dates, categories)
- ✅ Premium Alex Bender-inspired design

## Project Structure

```
/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── auth.py
│   │   ├── ai_agent.py
│   │   ├── sql_validator.py
│   │   └── plaid_integration.py
│   ├── databases/        # User database storage
│   │   ├── global.db
│   │   └── user_<id>/
│   ├── requirements.txt
│   └── .env
│
└── frontend/             # Next.js frontend
    ├── app/
    ├── components/
    ├── lib/
    └── public/
```

## Setup Instructions

### Backend Setup

1. Navigate to backend:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
OPENAI_API_KEY=your_openai_key
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox
JWT_SECRET=your_super_secret_jwt_key
```

5. Run backend:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run frontend:
```bash
npm run dev
```

5. Open browser:
```
http://localhost:3000
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Databases
- `GET /api/databases` - List user databases
- `POST /api/databases/create` - Create database via natural language
- `DELETE /api/databases/{db_id}` - Delete database

### Data Operations
- `POST /api/execute/sql` - Execute SQL query
- `POST /api/execute/natural` - Natural language command
- `GET /api/data/{db_id}` - Get all data from database
- `POST /api/data/{db_id}/insert` - Insert data via form

### AI Features
- `POST /api/ai/suggest-expiration` - Get expiration date suggestion
- `POST /api/ai/categorize` - Auto-categorize item

### Plaid
- `POST /api/plaid/create-link-token` - Get Plaid Link token
- `POST /api/plaid/exchange-token` - Exchange public token
- `POST /api/plaid/sync-transactions` - Import transactions

## Developer Notes

### What YOU Must Provide

1. API keys in `.env` files
2. Ensure `backend/databases/` folder exists
3. Secure hosting environment for deployment

### What Users Provide

1. Email + password for account
2. Natural language database descriptions
3. Optional: Plaid banking credentials

## Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ SQL injection prevention
- ✅ User isolation (users can only access their own data)
- ✅ Destructive operation confirmation
- ✅ Input validation and sanitization

## Design Philosophy

The UI follows the premium Alex Bender aesthetic:
- Soft white backgrounds with lilac/purple tints
- Floating 3D glass elements
- Smooth gradients and shadows
- Modern typography (Inter Tight)
- Generous whitespace
- Fluid animations

## License

MIT
