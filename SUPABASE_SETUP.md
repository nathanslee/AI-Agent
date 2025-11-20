# Supabase Deployment Guide - Step by Step

Follow this guide to deploy your AI Database Assistant with Supabase as your backend database!

## Prerequisites

- GitHub account (for code hosting and optional deployment)
- Supabase account (we'll create this)
- Your OpenAI API key ready
- Vercel account (for frontend deployment)

## What is Supabase?

Supabase is an open-source Firebase alternative that provides:
- PostgreSQL database (much more powerful than SQLite)
- Automatic backups
- Built-in authentication (optional for future use)
- Real-time subscriptions (optional for future use)
- RESTful APIs
- Free tier with generous limits

## Step 1: Create Supabase Project (3 minutes)

### 1.1 Sign Up for Supabase

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign in with GitHub (recommended) or email

### 1.2 Create New Project

1. Click "New Project"
2. Fill in details:
   - **Name**: `ai-database-assistant` (or your choice)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to your users (e.g., `us-east-1`)
   - **Plan**: Start with **Free tier** (includes 500MB database, 2GB bandwidth)
3. Click "Create new project"
4. Wait 2-3 minutes for provisioning

### 1.3 Get Your Connection Details

Once your project is ready:

1. Go to **Project Settings** (gear icon in sidebar)
2. Click **Database** in the left menu
3. Scroll to **Connection string** section
4. Select **URI** tab
5. Copy the connection string - it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.cgwkpnyzdjbsrgrqklxi.supabase.co:5432/postgres
   ```
6. Replace `[YOUR-PASSWORD]` with your actual database password

**Important:** Save this connection string - you'll need it for your backend!

## Step 2: Configure Your Backend for Supabase (2 minutes)

### 2.1 Update Backend Environment Variables

Navigate to your backend folder and create/update `.env`:

```bash
cd backend
```

Create `backend/.env` with these values:

```env
# Supabase Database Connection
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.cgwkpnyzdjbsrgrqklxi.supabase.co:5432/postgres

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# JWT Secret (generate a random 32+ character string)
JWT_SECRET=your-super-secret-jwt-key-at-least-32-characters-long

# Plaid (Optional - for banking features)
PLAID_CLIENT_ID=your-plaid-client-id-optional
PLAID_SECRET=your-plaid-secret-optional
PLAID_ENV=sandbox
```

**Replace:**
- `[YOUR-PASSWORD]` with your Supabase database password
- `sk-your-openai-api-key-here` with your actual OpenAI API key
- `your-super-secret-jwt-key-at-least-32-characters-long` with a random string

### 2.2 Install Updated Dependencies

The project now uses PostgreSQL instead of SQLite:

```bash
# Activate your virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install updated dependencies
pip install -r requirements.txt
```

### 2.3 Test Your Connection

Start your backend:

```bash
uvicorn app.main:app --reload --port 8000
```

If successful, you'll see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The tables will be automatically created on first startup!

Visit http://localhost:8000 - you should see:
```json
{
  "status": "healthy",
  "service": "AI Database Assistant API",
  "version": "1.0.0"
}
```

## Step 3: Verify Database Tables (1 minute)

### 3.1 Check Tables in Supabase Dashboard

1. Go to your Supabase project dashboard
2. Click **Table Editor** in the left sidebar
3. You should see these tables automatically created:
   - `users` - User accounts
   - `user_databases` - Database metadata
   - `plaid_tokens` - Plaid integration tokens

If you don't see them, check your backend logs for errors.

## Step 4: Deploy Frontend to Vercel (5 minutes)

### 4.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 4.2 Configure Frontend Environment

Navigate to frontend folder:
```bash
cd frontend
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PLAID_ENV=sandbox
```

### 4.3 Test Frontend Locally

```bash
npm install
npm run dev
```

Open http://localhost:3000 and test:
1. Create an account
2. Create a database
3. Add some data

### 4.4 Deploy Frontend to Vercel

From the frontend directory:

```bash
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name?** ai-database-assistant
- **Directory?** `./`
- **Override settings?** No

After deployment, add environment variables:

```bash
# Add your backend URL (you'll update this after deploying backend)
vercel env add NEXT_PUBLIC_API_URL
# Enter: http://localhost:8000 (temporary)

vercel env add NEXT_PUBLIC_PLAID_ENV
# Enter: sandbox
```

## Step 5: Deploy Backend (Choose One Option)

### Option A: Deploy to Vercel (Recommended for Simplicity)

Vercel can host both frontend and backend!

1. Create `backend/vercel.json`:
```json
{
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```

2. Deploy backend:
```bash
cd backend
vercel
```

3. Add environment variables in Vercel dashboard:
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `JWT_SECRET`
   - `PLAID_CLIENT_ID` (if using)
   - `PLAID_SECRET` (if using)
   - `PLAID_ENV`

### Option B: Deploy to Render

1. Go to https://render.com and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: ai-database-assistant-api
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Add environment variables (same as above)
6. Click "Create Web Service"

### Option C: Deploy to Fly.io

1. Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Create `backend/fly.toml`:
```toml
app = "ai-database-assistant"
primary_region = "iad"

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

3. Deploy:
```bash
fly launch
fly secrets set DATABASE_URL="your-supabase-url"
fly secrets set OPENAI_API_KEY="your-key"
fly secrets set JWT_SECRET="your-secret"
fly deploy
```

## Step 6: Connect Frontend to Deployed Backend (2 minutes)

Once your backend is deployed:

1. Get your backend URL (e.g., `https://your-app.vercel.app` or `https://your-app.onrender.com`)
2. Update frontend environment variable:

```bash
cd frontend
vercel env add NEXT_PUBLIC_API_URL production
# Enter your backend URL
```

3. Redeploy frontend:
```bash
vercel --prod
```

## Step 7: Test Your Live Application (2 minutes)

1. Open your Vercel frontend URL
2. Create a test account
3. Create a database: "Track my grocery items"
4. Add some data
5. Try natural language queries

## Database Management

### View Your Data

**Option 1: Supabase Dashboard**
1. Go to **Table Editor** in Supabase
2. Click on any table to view/edit data
3. You can run custom SQL queries in the **SQL Editor**

**Option 2: SQL Editor**
1. Click **SQL Editor** in Supabase sidebar
2. Write custom queries
3. Example:
```sql
-- View all users
SELECT * FROM users;

-- View all user databases
SELECT * FROM user_databases;

-- View a specific user's data
SELECT * FROM user_databases WHERE user_id = 'some-uuid';
```

### Backups

Supabase automatically backs up your database:
- **Free tier**: Daily backups (7 days retention)
- **Pro tier**: Point-in-time recovery

To create manual backup:
1. Go to **Database** → **Backups**
2. Click "Create backup"

### Database Performance

Monitor your database:
1. Go to **Database** → **Reports**
2. View metrics:
   - Query performance
   - Connection pooling
   - Storage usage
   - Active connections

## Scaling & Pricing

### Free Tier Limits
- 500 MB database storage
- 2 GB bandwidth
- 50,000 monthly active users
- 500 MB file storage
- Unlimited API requests

Perfect for development and small projects!

### When to Upgrade to Pro ($25/month)
- Need more than 500 MB database
- Want point-in-time recovery
- Need more than 2 GB bandwidth
- Want priority support

## Security Best Practices

### 1. Row Level Security (RLS) - Optional Advanced Feature

Supabase supports RLS for extra security:

```sql
-- Enable RLS on user tables
ALTER TABLE user_databases ENABLE ROW LEVEL SECURITY;

-- Create policy: users can only see their own databases
CREATE POLICY "Users can view own databases"
ON user_databases FOR SELECT
USING (auth.uid() = user_id);
```

**Note:** Your current app handles security in the backend, so RLS is optional.

### 2. Secure Your Connection String

- Never commit DATABASE_URL to git
- Use environment variables only
- Rotate database password periodically

### 3. Connection Pooling

Your app uses connection pooling (20 connections max) for better performance.

## Monitoring

### Supabase Dashboard
- **Database** → **Reports**: View performance metrics
- **Logs** → **Postgres Logs**: Debug database issues
- **API** → **Logs**: View API requests

### Backend Logs
- Vercel: Check function logs in dashboard
- Render: View logs in service page
- Fly.io: `fly logs`

## Troubleshooting

### "Could not connect to database"
- Check DATABASE_URL is correct
- Verify database password
- Check if IP is allowed (Supabase allows all by default)
- Look at backend logs for detailed error

### "Table does not exist"
- Check if backend started successfully
- Tables are created automatically on startup
- Check Supabase Table Editor to verify

### "Connection pool exhausted"
- Too many concurrent requests
- Increase pool size in `database.py`:
  ```python
  self.pool = SimpleConnectionPool(1, 50, self.database_url)  # Increase from 20 to 50
  ```

### "Slow queries"
- Check **Database** → **Reports** in Supabase
- Add indexes for frequently queried columns
- Optimize your SQL queries

## Migration from SQLite

If you have existing SQLite data to migrate:

1. Export SQLite data to CSV
2. Import to Supabase via **Table Editor**
3. Or use SQL to insert data

**Note:** Since the app creates per-user tables dynamically, migration is complex. Easier to start fresh with Supabase.

## Next Steps

1. Set up custom domain for frontend
2. Enable Supabase Authentication (optional enhancement)
3. Set up monitoring alerts
4. Configure automated backups
5. Add database indexes for performance

## Cost Breakdown

### Supabase
- **Free tier**: $0/month (500MB, 2GB bandwidth)
- **Pro tier**: $25/month (8GB, 50GB bandwidth, better support)

### Vercel
- **Hobby**: $0/month (personal projects)
- **Pro**: $20/month (production apps)

### OpenAI API
- **Database creation**: ~$0.01 each
- **Natural language queries**: ~$0.001 each
- **Estimate**: $1-5/month for moderate use

### Total
- **Development**: $0-5/month
- **Production**: $25-50/month

Much more cost-effective than managing your own database server!

## Support

- **Supabase Docs**: https://supabase.com/docs
- **Supabase Community**: https://github.com/supabase/supabase/discussions
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

## Success!

Your AI Database Assistant is now running on Supabase with:
- Managed PostgreSQL database
- Automatic backups
- Scalable infrastructure
- Built-in monitoring
- Enterprise-grade security

Share your app with users and start building!
