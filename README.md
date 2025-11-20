# DataBuddy

A premium full-stack AI-powered database assistant that lets users create and manage custom databases using natural language. Built with modern technologies and featuring a beautiful, responsive UI.

## 🎯 What Makes This Special

- **Zero SQL Required**: Create databases and query data using plain English
- **AI-Powered**: GPT-4o-mini generates schemas, SQL queries, and intelligent suggestions
- **Per-User Isolation**: Each user gets their own secure, isolated database tables
- **Banking Integration**: Sync transactions from your bank accounts via Plaid
- **Beautiful UI**: Premium design inspired by Alex Bender's aesthetic
- **Production-Ready**: Built with Supabase PostgreSQL, FastAPI, and Next.js 14

## 🚀 Quick Start

Want to get started immediately? Check out [QUICKSTART.md](QUICKSTART.md) for a streamlined setup guide!

For detailed Supabase setup instructions, see [SUPABASE_SETUP.md](SUPABASE_SETUP.md).

## Architecture

- **Frontend**: Next.js 14 (App Router) + TailwindCSS + shadcn/ui
- **Backend**: FastAPI + Python
- **Database**: Supabase PostgreSQL (per-user isolated tables)
- **AI**: OpenAI GPT-4o-mini
- **Banking**: Plaid API

## Features

### Core Features
- ✅ User authentication with JWT and bcrypt password hashing
- ✅ Per-user isolated database storage with Supabase PostgreSQL
- ✅ Natural language database creation using GPT-4o-mini
- ✅ Dynamic UI form generation based on schema
- ✅ AI-powered natural language to SQL query conversion
- ✅ Database management (create, delete, view)

### AI-Powered Features
- ✅ Smart schema generation from natural language descriptions
- ✅ Intelligent field suggestions and auto-population
- ✅ Auto-categorization of items
- ✅ Expiration date predictions for food items
- ✅ AI-generated descriptions for database entries
- ✅ Natural language query interface

### Schema Customization
- ✅ Add, remove, and edit database fields
- ✅ Enable/disable fields before creation
- ✅ User-friendly field type labels (Number, Text, Date, etc.)
- ✅ Optional vs required field configuration
- ✅ Real-time schema preview

### Banking Integration
- ✅ Plaid banking integration for transaction sync
- ✅ Automatic transaction mapping to database schema
- ✅ Secure token management

### Design & UX
- ✅ Premium Alex Bender-inspired design
- ✅ Custom hero image on landing page
- ✅ Smooth animations with Framer Motion
- ✅ Responsive design for mobile and desktop
- ✅ Glass morphism and 3D effects
- ✅ Modern typography with Inter Tight font

## Project Structure

```
/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py  # PostgreSQL/Supabase integration
│   │   ├── models.py
│   │   ├── auth.py
│   │   ├── ai_agent.py
│   │   ├── sql_validator.py
│   │   └── plaid_integration.py
│   ├── requirements.txt
│   └── .env             # Contains DATABASE_URL for Supabase
│
└── frontend/             # Next.js frontend
    ├── app/
    ├── components/
    ├── lib/
    └── public/
```

## Setup Instructions

### Backend Setup

1. **Set up Supabase** (see SUPABASE_SETUP.md for detailed guide):
   - Create account at https://supabase.com
   - Create new project
   - Get your DATABASE_URL from Project Settings → Database

2. Navigate to backend:
```bash
cd backend
```

3. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create `.env` file:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
OPENAI_API_KEY=your_openai_key
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox
JWT_SECRET=your_super_secret_jwt_key
```

6. Run backend:
```bash
uvicorn app.main:app --reload --port 8000
```

The database tables will be created automatically on first startup!

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

1. Supabase project and DATABASE_URL
2. API keys in `.env` files
3. Secure hosting environment for deployment (Vercel, Render, Fly.io, etc.)

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

## Credits

Initial codebase architecture and implementation assisted by Claude (Anthropic).

## License

MIT
