# 🚂 Railway Deployment Guide - Step by Step

Follow this guide to deploy your AI Database Assistant to Railway with persistent storage!

## Prerequisites

- GitHub account
- Railway account (we'll create this)
- Your OpenAI API key ready

## Step 1: Initialize Git Repository (5 minutes)

Open a terminal in your project root (`C:\Users\Nate\AI Agent\`):

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - AI Database Assistant"
```

## Step 2: Create GitHub Repository (3 minutes)

### Option A: Via GitHub Website (Easier)

1. Go to https://github.com/new
2. Repository name: `ai-database-assistant`
3. Set to **Private** (recommended for now)
4. **DON'T** initialize with README (we already have files)
5. Click "Create repository"

6. Back in your terminal, run the commands GitHub shows:
```bash
git remote add origin https://github.com/YOUR-USERNAME/ai-database-assistant.git
git branch -M main
git push -u origin main
```

### Option B: Via GitHub CLI (if you have it)

```bash
gh repo create ai-database-assistant --private --source=. --remote=origin --push
```

## Step 3: Sign Up for Railway (2 minutes)

1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your GitHub
4. You get **$5 free credit** to start!

## Step 4: Deploy Backend to Railway (5 minutes)

### 4.1 Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Select your `ai-database-assistant` repository
4. Railway will detect it's a Python app automatically

### 4.2 Configure Backend Service

1. Railway will start deploying - **STOP IT** (click the deployment to cancel)
2. Click on your service → **Settings** tab

**Set Root Directory:**
- Scroll to "Root Directory"
- Set to: `backend`
- Click "Update"

**Set Start Command:**
- Scroll to "Start Command"
- Set to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Click "Update"

### 4.3 Add Persistent Volume (Critical!)

1. In your service, click **"Variables"** tab
2. Click **"+ New Volume"**
3. Mount Path: `/app/databases`
4. Click "Add"

This ensures your databases persist between deployments! 🎉

### 4.4 Add Environment Variables

Click **"Variables"** tab → **"RAW Editor"** → Paste this:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
JWT_SECRET=your-super-secret-jwt-key-at-least-32-characters-long
PLAID_CLIENT_ID=your-plaid-client-id-optional
PLAID_SECRET=your-plaid-secret-optional
PLAID_ENV=sandbox
DATABASE_DIR=/app/databases
```

**Important:** Replace with your actual keys!

Click **"Update Variables"**

### 4.5 Deploy!

1. Go to **"Deployments"** tab
2. Click **"Deploy"** (or it will auto-deploy)
3. Wait 2-3 minutes for deployment
4. Click on the deployment to see logs

### 4.6 Get Your Backend URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://your-app.railway.app`)

**Test it:** Open your Railway URL in browser - you should see:
```json
{"status":"healthy","service":"AI Database Assistant API","version":"1.0.0"}
```

🎉 **Backend is live!**

## Step 5: Deploy Frontend to Vercel (5 minutes)

Vercel is perfect for Next.js apps (better than Railway for frontend).

### 5.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 5.2 Update Frontend Environment

Navigate to frontend folder:
```bash
cd frontend
```

Create/update `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-app.railway.app
NEXT_PUBLIC_PLAID_ENV=sandbox
```

**Replace `https://your-app.railway.app` with YOUR Railway backend URL!**

### 5.3 Deploy to Vercel

```bash
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name?** ai-database-assistant-frontend (or your choice)
- **Directory?** `./` (it's already in frontend folder)
- **Override settings?** No

Wait for deployment (1-2 minutes)...

### 5.4 Add Environment Variables to Vercel

After deployment, set production environment variables:

```bash
vercel env add NEXT_PUBLIC_API_URL
```
- Paste your Railway URL: `https://your-app.railway.app`
- Select: **Production**, **Preview**, **Development**

```bash
vercel env add NEXT_PUBLIC_PLAID_ENV
```
- Enter: `sandbox`
- Select: **Production**, **Preview**, **Development**

### 5.5 Redeploy with Environment Variables

```bash
vercel --prod
```

## Step 6: Test Your Live Application! (2 minutes)

1. Open your Vercel URL (shown in terminal after deployment)
2. Click **"Sign Up"**
3. Create an account
4. Create your first database!
5. Add some data
6. Try natural language commands

## Step 7: Update CORS for Production (Important!)

Now that you know your Vercel URL, let's secure CORS properly.

### 7.1 Update Backend CORS

Edit `backend/app/main.py` around line 26:

```python
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app",  # Add your actual Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7.2 Push Update

```bash
git add .
git commit -m "Update CORS for production"
git push
```

Railway will auto-deploy the update! ✨

## URLs Summary

After deployment, save these URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | `https://your-app.railway.app` | FastAPI backend |
| Frontend | `https://your-frontend.vercel.app` | Next.js app |
| Railway Dashboard | `https://railway.app/dashboard` | Monitor backend |
| Vercel Dashboard | `https://vercel.com/dashboard` | Monitor frontend |

## Cost Breakdown

### Railway Backend
- **Free Credit:** $5/month
- **After credit:** ~$5-10/month (pay as you go)
- Includes: Persistent volumes, automatic deployments, SSL

### Vercel Frontend
- **Free tier:** Unlimited deployments, 100GB bandwidth
- **Paid tier:** $20/month (if you exceed free tier)
- Most hobby projects stay free!

### OpenAI API
- **Database creation:** ~$0.01 each
- **Natural language queries:** ~$0.001 each
- **Estimate:** $1-5/month for moderate use

**Total:** ~$0-10/month for small-scale use, $20-30/month for production

## Monitoring Your App

### Check Backend Status

Railway Dashboard → Your Project → Backend Service:
- **Deployments:** See deployment history
- **Metrics:** CPU, Memory, Network usage
- **Logs:** See real-time logs (great for debugging)

### Check Frontend Status

Vercel Dashboard → Your Project:
- **Deployments:** See deployment history
- **Analytics:** Page views, performance
- **Logs:** Function logs

### Check Database Files

Railway doesn't provide direct file access, but you can:
1. Add an admin endpoint to download database files
2. Set up automated backups to S3
3. Use Railway CLI to access the container

## Troubleshooting

### Backend deployment failed
**Check logs:** Railway Dashboard → Deployments → Click failed deployment → View logs

**Common issues:**
- Missing environment variables → Add them in Variables tab
- Wrong start command → Check Settings tab
- Python version mismatch → Ensure `runtime.txt` says `python-3.11`

### Frontend can't connect to backend
**Check:**
- `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Backend URL is accessible (visit it in browser)
- CORS includes your Vercel domain

### "Could not validate credentials" error
- Clear browser localStorage
- Check JWT_SECRET is set in Railway
- Try creating a new account

### Database data disappeared
- Check that Volume is mounted at `/app/databases`
- Verify Volume exists in Railway dashboard
- Check deployment logs for errors

## Backup Your Production Database

Set up automated backups:

### Option 1: Manual Backup Endpoint (Add to backend)

```python
@app.get("/admin/backup")
async def backup_databases():
    """Create backup of all databases"""
    import shutil
    backup_path = shutil.make_archive("databases_backup", "zip", "./databases")
    return FileResponse(backup_path)
```

### Option 2: Railway Scheduled Backups (Recommended)

Use Railway Cron Jobs to backup to S3 daily (requires Railway Pro plan).

### Option 3: External Backup Service

Use services like:
- **Backblaze B2** ($0.005/GB)
- **AWS S3** ($0.023/GB)
- **Cloudflare R2** ($0.015/GB)

## Custom Domain (Optional)

### For Frontend (Vercel):
1. Vercel Dashboard → Your Project → Settings → Domains
2. Add your domain (e.g., `app.yourdomain.com`)
3. Update DNS records as shown

### For Backend (Railway):
1. Railway Dashboard → Your Service → Settings → Domains
2. Add custom domain (e.g., `api.yourdomain.com`)
3. Update DNS records as shown

## Environment Variables Cheat Sheet

### Backend (.env on Railway)
```env
OPENAI_API_KEY=sk-xxx                    # Required
JWT_SECRET=xxx                            # Required (32+ chars)
PLAID_CLIENT_ID=xxx                       # Optional
PLAID_SECRET=xxx                          # Optional
PLAID_ENV=sandbox                         # sandbox or production
DATABASE_DIR=/app/databases               # Required for Railway
```

### Frontend (.env.local on Vercel)
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app    # Required
NEXT_PUBLIC_PLAID_ENV=sandbox                           # Optional
```

## Success! 🎉

Your AI Database Assistant is now live with:
- ✅ Persistent database storage (Railway volumes)
- ✅ Automatic deployments (push to GitHub = auto-deploy)
- ✅ SSL/HTTPS (automatic)
- ✅ Global CDN (Vercel)
- ✅ Professional infrastructure

**Share your app:** Send your Vercel URL to friends!

## Next Steps

1. ✅ Set up a custom domain
2. ✅ Configure automated backups
3. ✅ Set up monitoring/alerts
4. ✅ Add analytics (Vercel Analytics)
5. ✅ Invite beta users!

## Support

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Issues?** Check logs in Railway/Vercel dashboards
