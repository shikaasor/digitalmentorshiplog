# Vercel Deployment Issues & Solutions

## Critical Issues Identified

### 1. **Frontend API URL Not Configured**

**Problem:** The frontend is using `http://localhost:8000` as the default API URL because `NEXT_PUBLIC_API_URL` is not set.

**Location:** `frontend/lib/api/client.ts:14`
```typescript
baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
```

**Solution:** Add this environment variable in Vercel dashboard:
- Variable: `NEXT_PUBLIC_API_URL`
- Value: `https://your-project-name.vercel.app/api`

---

### 2. **Missing Backend Environment Variables**

**Problem:** The backend requires several environment variables that must be configured in Vercel.

**Required Variables (from `backend/app/config.py`):**

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=mentorship-logs

# JWT (change in production!)
SECRET_KEY=your-production-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
```

**Solution:** Add ALL these variables in Vercel dashboard under Settings → Environment Variables

---

### 3. **Vercel.json Configuration Issues**

**Current Configuration Has Problems:**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.12"
  },
  "outputDirectory": "frontend/.next"
}
```

**Issues:**
- The `outputDirectory` is incorrect for a monorepo
- Routes may not properly handle Next.js routing
- Build configuration for Next.js might not work with subdirectory

**Better Configuration:**

```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm install && npm run build",
  "installCommand": "cd frontend && npm install",
  "outputDirectory": "frontend/.next",
  "functions": {
    "api/*.py": {
      "runtime": "python3.12"
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

---

### 4. **CORS Configuration (Already Fixed)**

**Status:** ✅ GOOD - Backend already includes Vercel domain
```python
ALLOWED_ORIGINS: Union[List[str], str] = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://mentorlog.vercel.app"
]
```

Make sure your actual Vercel deployment URL matches this!

---

### 5. **Python Dependencies**

**Status:** ✅ GOOD - `api/requirements.txt` includes all necessary packages including `mangum==0.19.0`

**Important:** Make sure `api/requirements.txt` is complete. It should include:
- All backend dependencies (from backend/requirements.txt)
- `mangum==0.19.0` for serverless adapter

---

### 6. **API Route Handler Import Path**

**Current Code in `api/index.py`:**
```python
from backend.app.main import app
```

**Potential Issue:** The import path might not resolve correctly in Vercel's serverless environment.

**Alternative (if above doesn't work):**
```python
import sys
import os

# More robust path setup
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from app.main import app  # Try without 'backend.' prefix
from mangum import Mangum

handler = Mangum(app, lifespan="off")
```

---

## Step-by-Step Deployment Checklist

### Before Deploying to Vercel:

1. **Update vercel.json** with the improved configuration above

2. **Set Environment Variables in Vercel Dashboard:**
   - Go to Project Settings → Environment Variables
   - Add ALL required backend environment variables
   - Add `NEXT_PUBLIC_API_URL` pointing to your Vercel domain + `/api`
   - Example: `NEXT_PUBLIC_API_URL=https://your-project.vercel.app/api`

3. **Verify CORS Configuration:**
   - Update `backend/app/config.py` line 25 to include your actual Vercel URL
   - Example: `https://your-actual-project-name.vercel.app`

4. **Verify api/requirements.txt:**
   - Must include all backend dependencies
   - Must include `mangum==0.19.0`

5. **Test Import Path (if needed):**
   - If you get import errors, try the alternative import path shown above

### During Deployment:

6. **Monitor Build Logs:**
   - Check for Python dependency installation errors
   - Check for Next.js build errors
   - Verify serverless function creation

7. **Test API Endpoints:**
   - After deployment, test: `https://your-project.vercel.app/api/health`
   - Should return: `{"status": "healthy"}`
   - If 500 error, check Vercel Function Logs

### After Deployment:

8. **Check Function Logs:**
   - Go to Vercel Dashboard → Deployments → Select deployment → Functions
   - Look for any errors in the `/api/index` function
   - Common errors:
     - Import errors → Fix path in api/index.py
     - Missing env vars → Add in Vercel settings
     - Database connection → Check DATABASE_URL

9. **Test Frontend API Calls:**
   - Open browser DevTools → Network tab
   - Try logging in
   - Check if requests go to correct URL (should be `/api/...` not `localhost:8000`)

10. **Fix CORS if needed:**
    - If you see CORS errors in browser console
    - Update ALLOWED_ORIGINS in backend/app/config.py
    - Redeploy

---

## Common Errors & Solutions

### Error: "Failed to fetch" or Network Error

**Cause:** Frontend is calling wrong API URL (localhost instead of Vercel)

**Solution:** Set `NEXT_PUBLIC_API_URL` environment variable in Vercel

---

### Error: "500 Internal Server Error" from /api/

**Cause:** Backend serverless function crashing

**Solution:**
1. Check Vercel Function Logs for specific error
2. Usually missing environment variables or import errors
3. Verify all env vars are set in Vercel dashboard

---

### Error: "Module 'backend.app.main' not found"

**Cause:** Import path issue in serverless environment

**Solution:** Try alternative import path:
```python
from app.main import app  # instead of from backend.app.main
```

---

### Error: CORS Policy Error in Browser

**Cause:** Vercel domain not in ALLOWED_ORIGINS

**Solution:** Update `backend/app/config.py` with your actual Vercel URL

---

## Quick Verification Commands

After deployment, test these URLs in your browser:

1. **Health Check:** `https://your-project.vercel.app/api/health`
   - Expected: `{"status": "healthy"}`

2. **API Root:** `https://your-project.vercel.app/api/`
   - Expected: `{"message": "Digital Mentorship Log API", "version": "1.0.0"}`

3. **API Docs:** `https://your-project.vercel.app/api/docs`
   - Expected: Interactive Swagger UI

If any of these fail, check Function Logs in Vercel Dashboard.

---

## Next Steps

1. Fix vercel.json configuration
2. Set all environment variables in Vercel
3. Redeploy
4. Test health endpoint
5. Test login functionality
6. Monitor Function Logs for any errors
