# ✅ Railway Deployment Checklist

## Before You Start

- [ ] OpenAI API Key ready (get it: https://platform.openai.com/api-keys)
- [ ] GitHub account (create at: https://github.com/signup)
- [ ] 30 minutes of time

## Step-by-Step Checklist

### 1. Git Setup (5 min)
```bash
cd "C:\Users\Nate\AI Agent"
git init
git add .
git commit -m "Initial commit"
```
- [ ] Git initialized
- [ ] Files committed

### 2. GitHub Setup (3 min)
- [ ] Go to https://github.com/new
- [ ] Name: `ai-database-assistant`
- [ ] Set to Private
- [ ] Click "Create repository"
- [ ] Copy the commands shown and run them:
```bash
git remote add origin https://github.com/YOUR-USERNAME/ai-database-assistant.git
git branch -M main
git push -u origin main
```
- [ ] Code pushed to GitHub

### 3. Railway Backend (8 min)

**Sign Up:**
- [ ] Go to https://railway.app
- [ ] Click "Login with GitHub"
- [ ] Authorize Railway

**Deploy:**
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Select `ai-database-assistant`
- [ ] Click your service when it appears

**Configure:**
- [ ] Settings → Root Directory → Set to `backend`
- [ ] Settings → Start Command → Set to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Click "New Volume" → Mount Path: `/app/databases` → Add

**Environment Variables:**
- [ ] Click "Variables" tab
- [ ] Click "RAW Editor"
- [ ] Paste this (with YOUR keys!):
```env
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET=your-secret-at-least-32-chars
DATABASE_DIR=/app/databases
```
- [ ] Click "Update Variables"

**Get URL:**
- [ ] Settings → Domains → "Generate Domain"
- [ ] Copy URL (save it!) → `https://________.railway.app`
- [ ] Test it in browser (should see health check)

### 4. Frontend Setup (5 min)

**Update Environment:**
```bash
cd frontend
```

Create `.env.local` with:
```env
NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-URL-HERE.railway.app
```
- [ ] `.env.local` created with Railway URL

**Install Vercel:**
```bash
npm install -g vercel
```
- [ ] Vercel CLI installed

**Deploy:**
```bash
vercel
```
- [ ] Follow prompts (choose your account, name project, etc.)
- [ ] Deployment complete

**Add Environment Variables:**
```bash
vercel env add NEXT_PUBLIC_API_URL
# Paste your Railway URL, select all environments

vercel env add NEXT_PUBLIC_PLAID_ENV
# Type: sandbox, select all environments
```
- [ ] Environment variables added

**Deploy to Production:**
```bash
vercel --prod
```
- [ ] Production deployment complete
- [ ] Copy Vercel URL → `https://________.vercel.app`

### 5. Test Everything! (5 min)

- [ ] Open your Vercel URL
- [ ] Sign up for an account
- [ ] Create a test database
- [ ] Add some data via form
- [ ] Try a natural language command
- [ ] View the table data

## 🎉 Success Checklist

If all these work, you're live!

- [ ] Backend health check works
- [ ] Frontend loads
- [ ] Can create account
- [ ] Can login
- [ ] Can create database
- [ ] Can add data
- [ ] Natural language commands work
- [ ] Data persists after refresh

## Your Live URLs

**Backend API:**
`https://________________.railway.app`

**Frontend App:**
`https://________________.vercel.app`

**Share with friends!** 🚀

## If Something Breaks

1. **Check Railway Logs:**
   - Railway Dashboard → Your Project → Deployments → Click deployment → Logs

2. **Check Vercel Logs:**
   - Vercel Dashboard → Your Project → Deployments → Click deployment → Logs

3. **Check Browser Console:**
   - Right-click → Inspect → Console tab

4. **Common Fixes:**
   - Backend 500 error → Check environment variables in Railway
   - Frontend can't connect → Check `NEXT_PUBLIC_API_URL` in Vercel
   - CORS error → Check backend logs, verify Vercel URL is in CORS list

## Next Steps After Deployment

- [ ] Set up custom domain (optional)
- [ ] Configure automated backups
- [ ] Set up monitoring alerts
- [ ] Share with beta users
- [ ] Collect feedback

## Cost Tracking

**Check spending:**
- Railway: https://railway.app/account/billing
- Vercel: https://vercel.com/account/billing
- OpenAI: https://platform.openai.com/usage

**Set spending limits:**
- OpenAI Dashboard → Settings → Billing → Set monthly limit

## Support

Need help?
- Read `RAILWAY_SETUP.md` for detailed guide
- Check Railway docs: https://docs.railway.app
- Check Vercel docs: https://vercel.com/docs
