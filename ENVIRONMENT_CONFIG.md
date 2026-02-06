# 🔧 Environment Configuration Guide

## Overview

This project uses environment variables for different deployment environments. This guide explains how to configure each environment.

---

## 📁 Environment Files

### Backend Environment (`.env`)
Location: `/app/backend/.env`

### Frontend Environment (`.env`)
Location: `/app/frontend/.env`

---

## 🏠 Local Development

### Backend (`/app/backend/.env`)

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=campus_agent
EMERGENT_LLM_KEY=sk-emergent-0685e9f564833D317A
CORS_ORIGINS=*
```

### Frontend (`/app/frontend/.env`)

```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

### Start Local Services

```bash
# Terminal 1 - MongoDB
sudo supervisorctl start mongodb

# Terminal 2 - Backend
cd /app/backend
sudo supervisorctl start backend

# Terminal 3 - Frontend
cd /app/frontend
sudo supervisorctl start frontend
```

---

## ☁️ Production (Cloud Deployment)

### MongoDB Atlas

**Connection String Format:**
```
mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/DATABASE?retryWrites=true&w=majority
```

**Example:**
```
mongodb+srv://campus_admin:MySecurePass123@campus-cluster.abc123.mongodb.net/campus_agent?retryWrites=true&w=majority
```

**⚠️ Important:**
- Replace `USERNAME` with your MongoDB Atlas username
- Replace `PASSWORD` with your actual password
- Replace `CLUSTER` with your cluster URL
- Replace `DATABASE` with `campus_agent`

### Render Backend Environment Variables

Add these in Render Dashboard → Environment:

```
MONGO_URL=mongodb+srv://campus_admin:YOUR_PASSWORD@campus-cluster.xxxxx.mongodb.net/campus_agent?retryWrites=true&w=majority

DB_NAME=campus_agent

EMERGENT_LLM_KEY=sk-emergent-0685e9f564833D317A

CORS_ORIGINS=https://your-app.vercel.app
```

**⚠️ Update CORS_ORIGINS after Vercel deployment!**

### Vercel Frontend Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

```
REACT_APP_BACKEND_URL=https://your-backend-name.onrender.com
```

**⚠️ Important:**
- Do NOT include `/api` at the end
- Use your actual Render backend URL
- No trailing slash

---

## 🔐 Security Best Practices

### 1. Never Commit Secrets

Add to `.gitignore`:
```
.env
.env.local
.env.production
*.pem
*.key
```

### 2. Use .env.example Files

Provide templates without actual secrets:

**Backend `.env.example`:**
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=campus_agent
EMERGENT_LLM_KEY=your-emergent-llm-key-here
CORS_ORIGINS=*
```

**Frontend `.env.example`:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

### 3. Rotate Keys Regularly

- Change MongoDB password every 90 days
- Rotate API keys quarterly
- Update all deployment environments

### 4. Restrict CORS

**Development:**
```
CORS_ORIGINS=*
```

**Production:**
```
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

---

## 🧪 Testing Environment

For staging/testing deployments:

### Backend
```env
MONGO_URL=mongodb+srv://...test-cluster...
DB_NAME=campus_agent_test
EMERGENT_LLM_KEY=sk-emergent-...
CORS_ORIGINS=https://your-app-staging.vercel.app
```

### Frontend
```env
REACT_APP_BACKEND_URL=https://your-backend-staging.onrender.com
```

---

## 📊 Environment Variable Reference

### Backend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MONGO_URL` | ✅ Yes | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | ✅ Yes | Database name | `campus_agent` |
| `EMERGENT_LLM_KEY` | ✅ Yes | LLM API key | `sk-emergent-...` |
| `CORS_ORIGINS` | ✅ Yes | Allowed origins | `*` or `https://app.vercel.app` |

### Frontend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | ✅ Yes | Backend API URL | `http://localhost:8001` |
| `WDS_SOCKET_PORT` | ❌ No | WebSocket port | `443` |
| `ENABLE_HEALTH_CHECK` | ❌ No | Health check | `false` |

---

## 🔄 Updating Environment Variables

### Render

1. Go to Render Dashboard
2. Select your service
3. Click **"Environment"**
4. Edit or add variables
5. Click **"Save Changes"**
6. Service will **automatically redeploy**

### Vercel

1. Go to Vercel Dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Edit or add variables
5. Click **"Save"**
6. **Redeploy** your project:
   - Go to **Deployments**
   - Click **"..."** on latest deployment
   - Click **"Redeploy"**

---

## ⚠️ Common Issues

### Issue 1: "Cannot connect to MongoDB"

**Causes:**
- Wrong MONGO_URL
- Password contains special characters
- Network access not configured

**Solutions:**
1. Verify connection string format
2. URL-encode password if it has special characters
3. Check MongoDB Atlas Network Access allows your IP
4. Test connection string locally first

### Issue 2: "CORS policy error"

**Cause:** Backend CORS_ORIGINS doesn't include frontend URL

**Solution:**
1. Update `CORS_ORIGINS` in Render to include Vercel URL
2. Wait for redeploy
3. Clear browser cache
4. Try again

### Issue 3: "API calls return undefined"

**Cause:** Wrong `REACT_APP_BACKEND_URL`

**Solution:**
1. Verify URL in Vercel environment variables
2. Ensure no `/api` at the end
3. Ensure no trailing slash
4. Redeploy frontend

### Issue 4: "LLM API errors"

**Causes:**
- Invalid EMERGENT_LLM_KEY
- Insufficient credits
- Rate limiting

**Solutions:**
1. Verify key is correct
2. Check key balance/credits
3. Test key with a simple request
4. Check Render logs for specific error

---

## 🎯 Quick Start Commands

### Check Environment Variables

**Backend (local):**
```bash
cd /app/backend
cat .env
```

**Frontend (local):**
```bash
cd /app/frontend
cat .env
```

### Test With Environment Variables

**Backend:**
```bash
cd /app/backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.environ.get('MONGO_URL'))"
```

**Frontend:**
```bash
cd /app/frontend
echo $REACT_APP_BACKEND_URL
```

---

## 📝 Environment Checklist

Before deploying, verify:

### Backend
- [ ] MONGO_URL is valid and tested
- [ ] DB_NAME is set to `campus_agent`
- [ ] EMERGENT_LLM_KEY is valid
- [ ] CORS_ORIGINS includes frontend URL (production)

### Frontend
- [ ] REACT_APP_BACKEND_URL points to correct backend
- [ ] URL has no trailing `/api`
- [ ] URL has no trailing slash

### MongoDB Atlas
- [ ] Cluster is created and running
- [ ] Database user exists with password
- [ ] Network access allows connections
- [ ] Connection string is correct

---

## 🆘 Getting Help

**Environment Variable Issues:**
- Check service-specific logs (Render/Vercel)
- Verify syntax (no spaces, quotes if needed)
- Test locally first before cloud deployment

**Connection Issues:**
- Use `curl` to test backend endpoints
- Check browser console for frontend errors
- Verify all services are running

---

## ✅ Success Indicators

### Backend Working
```bash
curl https://your-backend.onrender.com/api/
# Should return: {"message": "College Campus AI Agent API", "status": "operational"}
```

### Frontend Working
- Open `https://your-app.vercel.app`
- Should see chat interface
- No console errors
- Can send messages and get responses

### End-to-End Working
- Chat receives AI responses
- Events tab shows data
- Facilities tab shows data
- Bookings can be created

**All green? You're fully configured! 🎉**
