# AI Database Assistant - Deployment Guide

Complete step-by-step guide to deploy your AI Database Assistant.

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- OpenAI API key
- Plaid API credentials (optional)

## Part 1: Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Python Virtual Environment

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

Create `backend/.env` file:

```env
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Plaid Configuration (Optional - for banking integration)
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox

# JWT Secret (REQUIRED - use a strong random string)
JWT_SECRET=your-super-secret-jwt-key-at-least-32-characters

# Database Directory
DATABASE_DIR=./databases
```

**How to get your API keys:**

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and paste it in your `.env` file

**Plaid API Credentials (Optional):**
1. Go to https://dashboard.plaid.com/signup
2. Create a free account
3. Get your Client ID and Secret from the dashboard
4. Use "sandbox" environment for testing

**JWT Secret:**
Generate a secure random string (32+ characters). You can use:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Create Database Directory

```bash
mkdir databases
```

### 6. Test Backend

```bash
uvicorn app.main:app --reload --port 8000
```

Open browser to http://localhost:8000 - you should see:
```json
{"status":"healthy","service":"AI Database Assistant API","version":"1.0.0"}
```

## Part 2: Frontend Setup

### 1. Navigate to Frontend Directory

Open a NEW terminal window and navigate:

```bash
cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

### 3. Create Environment File

Create `frontend/.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PLAID_ENV=sandbox
```

### 4. Test Frontend

```bash
npm run dev
```

Open browser to http://localhost:3000 - you should see the landing page!

## Part 3: Testing the Full Application

### 1. Keep Both Servers Running

- Terminal 1: Backend (port 8000)
- Terminal 2: Frontend (port 3000)

### 2. Create Your First Account

1. Open http://localhost:3000
2. Click "Sign Up"
3. Enter email and password
4. You'll be redirected to the dashboard

### 3. Create Your First Database

1. Click "Create New Database"
2. Describe what you want to track (e.g., "Track grocery items with name, store, date, and expiration")
3. Click "Generate Database"
4. Review the AI-generated schema
5. Click "Create Database"

### 4. Add Data

1. Click on your new database
2. Use the "Add Data" tab to insert records via form
3. Or use "Natural Language" tab to add data with commands like:
   - "Add bananas bought today at Trader Joe's"
   - "Show me all items"
   - "Add milk, expires in 7 days"

## Part 4: Production Deployment

### Backend Deployment Options

#### Option A: Railway.app (Recommended)

1. Create account at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables in Railway dashboard
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Option B: Heroku

1. Install Heroku CLI
2. Create `Procfile` in backend folder:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

#### Option C: DigitalOcean App Platform

1. Create account at https://www.digitalocean.com
2. Click "Create" → "Apps"
3. Connect GitHub repository
4. Configure build and run commands
5. Add environment variables

### Frontend Deployment Options

#### Option A: Vercel (Recommended)

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Navigate to frontend folder:
   ```bash
   cd frontend
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Add environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` = your backend URL

#### Option B: Netlify

1. Install Netlify CLI:
   ```bash
   npm i -g netlify-cli
   ```

2. Build and deploy:
   ```bash
   cd frontend
   npm run build
   netlify deploy --prod
   ```

### Update Environment Variables for Production

**Backend `.env`:**
```env
OPENAI_API_KEY=your-production-key
PLAID_ENV=production  # If using Plaid in production
JWT_SECRET=your-secure-production-secret
```

**Frontend `.env.local`:**
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_PLAID_ENV=production
```

## Part 5: Security Checklist

Before deploying to production:

- [ ] Use strong JWT secret (32+ characters)
- [ ] Enable HTTPS on both frontend and backend
- [ ] Update CORS origins in `backend/app/main.py` to your production domains
- [ ] Use production Plaid environment (if using Plaid)
- [ ] Set secure password requirements
- [ ] Regularly backup the `databases/` folder
- [ ] Monitor API usage and costs
- [ ] Set up error logging (Sentry recommended)

## Part 6: Troubleshooting

### Backend won't start

**Error: "No module named 'fastapi'"**
- Solution: Activate virtual environment and run `pip install -r requirements.txt`

**Error: "OPENAI_API_KEY not found"**
- Solution: Create `.env` file in backend folder with your API key

### Frontend won't start

**Error: "Module not found"**
- Solution: Run `npm install` in frontend folder

**Error: "API request failed"**
- Solution: Check that backend is running on port 8000

### Database creation fails

**Error: "Failed to generate schema"**
- Solution: Verify OpenAI API key is valid and has credits

**Error: "Permission denied"**
- Solution: Ensure `databases/` folder exists and is writable

### Authentication issues

**Error: "Could not validate credentials"**
- Solution: Clear browser localStorage and login again

## Part 7: Ongoing Maintenance

### Backup Your Data

Regularly backup the `backend/databases/` folder:

```bash
# Create backup
tar -czf databases-backup-$(date +%Y%m%d).tar.gz backend/databases/

# Restore backup
tar -xzf databases-backup-20250214.tar.gz
```

### Monitor Costs

- OpenAI API: Monitor usage at https://platform.openai.com/usage
- Set spending limits in OpenAI dashboard
- Track Plaid API calls if using banking features

### Update Dependencies

**Backend:**
```bash
cd backend
pip list --outdated
pip install --upgrade package-name
```

**Frontend:**
```bash
cd frontend
npm outdated
npm update
```

## Part 8: Feature Extensions

### Add Email Verification

Install: `pip install fastapi-mail`

### Add File Uploads

Install: `pip install python-multipart`

### Add Data Export

Already supported - use natural language commands like:
- "Show me all records"
- Copy results from table view

### Connect More Banks

Plaid supports 10,000+ financial institutions automatically!

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs: `uvicorn app.main:app --reload --log-level debug`
3. Check browser console for frontend errors
4. Review API documentation at http://localhost:8000/docs

## Success!

Your AI Database Assistant is now running! Create databases, add data, and let AI help you manage everything with natural language.

Happy building! 🚀
