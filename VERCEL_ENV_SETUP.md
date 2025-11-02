# Vercel Environment Variables Setup Guide

This guide will help you configure all necessary environment variables in Vercel for both frontend and backend.

## Step 1: Access Vercel Environment Variables

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Select your project
3. Click on "Settings" tab
4. Click on "Environment Variables" in the left sidebar

## Step 2: Add Frontend Environment Variables

Add these variables for the **Production**, **Preview**, and **Development** environments:

### NEXT_PUBLIC_API_URL
- **Key:** `NEXT_PUBLIC_API_URL`
- **Value:** `https://your-actual-project-name.vercel.app/api`
- **Important:** Replace `your-actual-project-name` with your actual Vercel project domain
- **Environments:** Production, Preview, Development

### Supabase Frontend Variables (Optional)
If your frontend needs direct Supabase access:

- **Key:** `NEXT_PUBLIC_SUPABASE_URL`
- **Value:** Your Supabase project URL (e.g., `https://xxxxx.supabase.co`)
- **Environments:** Production, Preview, Development

- **Key:** `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **Value:** Your Supabase anon/public key
- **Environments:** Production, Preview, Development

## Step 3: Add Backend Environment Variables

Add these variables for **Production**, **Preview**, and **Development** environments:

### Database Configuration

**DATABASE_URL**
- **Key:** `DATABASE_URL`
- **Value:** `postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres`
- **Where to get it:**
  1. Go to Supabase dashboard
  2. Select your project
  3. Go to Settings → Database
  4. Copy the "URI" connection string under "Connection string"
- **Environments:** Production, Preview, Development

### Supabase Configuration

**SUPABASE_URL**
- **Key:** `SUPABASE_URL`
- **Value:** `https://xxxxx.supabase.co`
- **Where to get it:** Supabase → Settings → API → Project URL
- **Environments:** Production, Preview, Development

**SUPABASE_KEY**
- **Key:** `SUPABASE_KEY`
- **Value:** Your anon/public key
- **Where to get it:** Supabase → Settings → API → Project API keys → `anon` `public`
- **Environments:** Production, Preview, Development

**SUPABASE_SERVICE_ROLE_KEY**
- **Key:** `SUPABASE_SERVICE_ROLE_KEY`
- **Value:** Your service role key
- **Where to get it:** Supabase → Settings → API → Project API keys → `service_role` (click "Reveal" to see it)
- **⚠️ IMPORTANT:** This is a SECRET key with admin privileges. Keep it secure!
- **Environments:** Production, Preview, Development

**SUPABASE_STORAGE_BUCKET**
- **Key:** `SUPABASE_STORAGE_BUCKET`
- **Value:** `mentorship-logs` (or whatever you named your storage bucket)
- **Where to create:**
  1. Go to Supabase → Storage
  2. Create a new bucket named `mentorship-logs`
  3. Make it private (for security)
- **Environments:** Production, Preview, Development

### JWT Configuration

**SECRET_KEY**
- **Key:** `SECRET_KEY`
- **Value:** A secure random string (minimum 32 characters)
- **How to generate:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  Or use an online generator: https://randomkeygen.com/
- **⚠️ IMPORTANT:** Use a DIFFERENT key for production than development!
- **Environments:** Production, Preview, Development

**ALGORITHM**
- **Key:** `ALGORITHM`
- **Value:** `HS256`
- **Environments:** Production, Preview, Development

**ACCESS_TOKEN_EXPIRE_HOURS**
- **Key:** `ACCESS_TOKEN_EXPIRE_HOURS`
- **Value:** `24`
- **Environments:** Production, Preview, Development

### Optional: Email Configuration

Only add these if you plan to use email features:

- **SMTP_HOST:** `smtp.gmail.com`
- **SMTP_PORT:** `587`
- **SMTP_USER:** Your email address
- **SMTP_PASSWORD:** Your app-specific password (not your regular Gmail password)

## Step 4: Verify Environment Variables

After adding all variables, your Vercel environment variables should look like this:

```
NEXT_PUBLIC_API_URL = https://your-project.vercel.app/api
DATABASE_URL = postgresql://postgres:...@db.xxxxx.supabase.co:5432/postgres
SUPABASE_URL = https://xxxxx.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_STORAGE_BUCKET = mentorship-logs
SECRET_KEY = your-generated-secret-key-here
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_HOURS = 24
```

## Step 5: Update Backend CORS Configuration

After you know your Vercel deployment URL:

1. Open `backend/app/config.py`
2. Update line 25 to include your actual Vercel URL:
   ```python
   ALLOWED_ORIGINS: Union[List[str], str] = [
       "http://localhost:3000",
       "http://localhost:8000",
       "https://your-actual-project-name.vercel.app"  # ← Add this
   ]
   ```
3. Commit and push the change
4. Vercel will automatically redeploy

## Step 6: Redeploy

After adding all environment variables:

1. Go to Vercel Dashboard → Deployments
2. Click on the latest deployment
3. Click "Redeploy" button
4. OR push a new commit to trigger automatic deployment

## Step 7: Test Deployment

After redeployment, test these endpoints:

### 1. API Health Check
Visit: `https://your-project.vercel.app/api/health`

**Expected response:**
```json
{"status": "healthy"}
```

**If you get an error:**
- Check Vercel Function Logs (Dashboard → Functions → api/index)
- Verify all environment variables are set correctly

### 2. API Root
Visit: `https://your-project.vercel.app/api/`

**Expected response:**
```json
{
  "message": "Digital Mentorship Log API",
  "version": "1.0.0"
}
```

### 3. API Documentation
Visit: `https://your-project.vercel.app/api/docs`

**Expected:** Interactive Swagger UI

### 4. Frontend Login
Visit: `https://your-project.vercel.app/auth/login`

1. Try logging in with valid credentials
2. Open browser DevTools → Network tab
3. Check that API calls go to `/api/...` not `localhost:8000`
4. Verify successful authentication

## Troubleshooting

### Problem: "Failed to fetch" in browser console

**Cause:** `NEXT_PUBLIC_API_URL` not set or incorrect

**Solution:**
1. Verify `NEXT_PUBLIC_API_URL` is set in Vercel
2. Make sure it points to `https://your-domain.vercel.app/api`
3. Redeploy after setting

### Problem: "500 Internal Server Error" from API

**Cause:** Missing backend environment variables or database connection issue

**Solution:**
1. Check Vercel Function Logs for specific error
2. Verify ALL backend env vars are set
3. Test database connection by trying the health endpoint

### Problem: CORS errors in browser

**Cause:** Vercel domain not in ALLOWED_ORIGINS

**Solution:**
1. Update `backend/app/config.py` with your Vercel URL
2. Commit and push
3. Wait for automatic redeploy

### Problem: "Module not found" error in Function Logs

**Cause:** Import path issue in `api/index.py`

**Solution:**
Try alternative import path in `api/index.py`:
```python
from app.main import app  # instead of from backend.app.main
```

## Security Notes

🔒 **Never commit these to git:**
- `.env` files (already in .gitignore)
- `SUPABASE_SERVICE_ROLE_KEY`
- `SECRET_KEY`
- Database passwords
- Any API keys or secrets

✅ **Safe to commit:**
- `.env.example` files (template with dummy values)
- Configuration files without secrets
- Vercel configuration (vercel.json)

## Quick Copy-Paste Checklist

Use this checklist when setting up a new deployment:

```
Frontend Environment Variables:
☐ NEXT_PUBLIC_API_URL

Backend Environment Variables:
☐ DATABASE_URL
☐ SUPABASE_URL
☐ SUPABASE_KEY
☐ SUPABASE_SERVICE_ROLE_KEY
☐ SUPABASE_STORAGE_BUCKET
☐ SECRET_KEY (generate new for production!)
☐ ALGORITHM
☐ ACCESS_TOKEN_EXPIRE_HOURS

Code Changes:
☐ Update ALLOWED_ORIGINS in backend/app/config.py
☐ Commit and push changes

Verification:
☐ Test /api/health endpoint
☐ Test /api/ endpoint
☐ Test /api/docs endpoint
☐ Test frontend login functionality
☐ Check browser console for errors
☐ Check Vercel Function Logs
```
