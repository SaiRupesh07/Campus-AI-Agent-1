# 🚀 Production Deployment Guide

## College Campus AI Agent - Free Deployment Stack

Deploy your complete AI agent to production **100% FREE** using:
- **Frontend**: Vercel (Free)
- **Backend**: Render (Free)
- **Database**: MongoDB Atlas (Free)

---

## 🎯 Deployment Architecture

```
User Browser
     ↓
Vercel (React Frontend)
https://campus-ai-agent.vercel.app
     ↓
Render (FastAPI Backend)
https://campus-ai-agent.onrender.com
     ↓
MongoDB Atlas (Cloud Database)
mongodb+srv://...
     ↓
OpenAI API (via Emergent LLM Key)
```

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:
- [ ] GitHub account
- [ ] MongoDB Atlas account
- [ ] Render account
- [ ] Vercel account
- [ ] Emergent LLM Key (or OpenAI API key)
- [ ] Project pushed to GitHub repository

---

## 🟣 STEP 1: Setup MongoDB Atlas (Free Cloud Database)

### 1.1 Create MongoDB Atlas Account

1. Go to: https://www.mongodb.com/atlas
2. Click **"Try Free"**
3. Sign up with email or Google
4. Verify your email

### 1.2 Create Free Cluster

1. After login, click **"Build a Database"**
2. Choose **"Shared"** (Free tier - M0)
3. Select:
   - **Cloud Provider**: AWS (or any)
   - **Region**: Closest to your users
   - **Cluster Name**: `campus-agent-cluster`
4. Click **"Create Cluster"**
5. Wait 3-5 minutes for creation

### 1.3 Create Database User

1. Go to **"Database Access"** (left sidebar)
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Set:
   - **Username**: `campus_admin`
   - **Password**: Generate a strong password (SAVE THIS!)
5. **Database User Privileges**: Read and write to any database
6. Click **"Add User"**

### 1.4 Setup Network Access

1. Go to **"Network Access"** (left sidebar)
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (for development)
   - This adds `0.0.0.0/0`
   - ⚠️ For production, restrict to Render's IPs later
4. Click **"Confirm"**

### 1.5 Get Connection String

1. Go to **"Database"** (left sidebar)
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. **Driver**: Python
5. **Version**: 3.6 or later
6. Copy the connection string:

```
mongodb+srv://campus_admin:<password>@campus-agent-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

7. **Replace `<password>`** with your actual password
8. **Add database name** after `.mongodb.net/`:

```
mongodb+srv://campus_admin:YOUR_PASSWORD@campus-agent-cluster.xxxxx.mongodb.net/campus_agent?retryWrites=true&w=majority
```

9. **SAVE THIS CONNECTION STRING** - you'll need it for Render

---

## 🔵 STEP 2: Deploy Backend on Render (Free)

### 2.1 Prepare Your Repository

Make sure your GitHub repository has:
```
your-repo/
├── backend/
│   ├── server.py
│   └── requirements.txt
├── frontend/
│   └── ...
├── render.yaml
└── Procfile
```

The `render.yaml` and `Procfile` are already created in your project.

### 2.2 Create Render Account

1. Go to: https://render.com
2. Click **"Get Started"**
3. **Sign in with GitHub**
4. Authorize Render to access your repositories

### 2.3 Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. If not listed, click **"Configure account"** and grant access

### 2.4 Configure Web Service

Fill in the settings:

| Setting | Value |
|---------|-------|
| **Name** | `campus-ai-agent-backend` |
| **Region** | Oregon (US West) or closest |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `uvicorn backend.server:app --host 0.0.0.0 --port 10000` |
| **Instance Type** | `Free` |

### 2.5 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these 4 variables:

1. **MONGO_URL**
   ```
   mongodb+srv://campus_admin:YOUR_PASSWORD@campus-agent-cluster.xxxxx.mongodb.net/campus_agent?retryWrites=true&w=majority
   ```
   (Your MongoDB connection string from Step 1.5)

2. **DB_NAME**
   ```
   campus_agent
   ```

3. **EMERGENT_LLM_KEY**
   ```
   sk-emergent-0685e9f564833D317A
   ```
   (Or your own OpenAI API key)

4. **CORS_ORIGINS**
   ```
   *
   ```
   (Later update with your Vercel domain)

### 2.6 Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Build your application (~3-5 minutes)
   - Deploy it
   - Give you a URL like: `https://campus-ai-agent-backend.onrender.com`

3. **Wait for deployment** - Watch the logs
4. Look for: `✓ Build successful` and `✓ Deployment successful`

### 2.7 Test Backend Deployment

Once deployed, test your backend:

1. Open: `https://your-backend-url.onrender.com/api/`

   Expected response:
   ```json
   {
     "message": "College Campus AI Agent API",
     "status": "operational",
     "version": "1.0.0"
   }
   ```

2. Test API docs: `https://your-backend-url.onrender.com/docs`

3. Test events endpoint: `https://your-backend-url.onrender.com/api/events`

**✅ If you see data, backend is working!**

**⚠️ Important Notes about Render Free Tier:**
- Service **spins down after 15 minutes of inactivity**
- First request after spin down takes 30-60 seconds
- This is normal for free tier
- Consider upgrading to paid tier for production

**Save your backend URL** - you'll need it for frontend deployment!

---

## 🟢 STEP 3: Deploy Frontend on Vercel (Free)

### 3.1 Prepare Frontend

Ensure `frontend/src/App.js` uses environment variable (already done):

```javascript
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
```

### 3.2 Create Vercel Account

1. Go to: https://vercel.com
2. Click **"Sign Up"**
3. **Sign in with GitHub**
4. Authorize Vercel

### 3.3 Import Project

1. Click **"Add New..."** → **"Project"**
2. **Import Git Repository**
3. Select your repository
4. Click **"Import"**

### 3.4 Configure Project

1. **Framework Preset**: `Create React App`
2. **Root Directory**: `frontend`
   - Click **"Edit"**
   - Enter: `frontend`
   - Click **"Continue"**

3. **Build and Output Settings**:
   - **Build Command**: `yarn build` (auto-detected)
   - **Output Directory**: `build` (auto-detected)
   - **Install Command**: `yarn install` (auto-detected)

### 3.5 Add Environment Variable

Click **"Environment Variables"** section:

Add:

**Key**: `REACT_APP_BACKEND_URL`

**Value**: `https://your-backend-url.onrender.com`
(Your Render backend URL from Step 2)

**Example**:
```
https://campus-ai-agent-backend.onrender.com
```

⚠️ **Important**: Do NOT include `/api` at the end!

### 3.6 Deploy

1. Click **"Deploy"**
2. Vercel will:
   - Install dependencies (~2 minutes)
   - Build your React app (~1-2 minutes)
   - Deploy it globally
3. Wait for: **"Congratulations! Your project has been successfully deployed."**

### 3.7 Get Your Live URL

Your frontend will be live at:
```
https://your-project-name.vercel.app
```

Or a custom domain like:
```
https://campus-ai-agent.vercel.app
```

**✅ Open this URL in your browser!**

---

## 🔄 STEP 4: Update CORS (Important!)

Now that you have your Vercel URL, update backend CORS:

### 4.1 Update Render Environment Variable

1. Go to Render dashboard
2. Select your backend service
3. Go to **"Environment"**
4. Edit **CORS_ORIGINS**:

   **Before**:
   ```
   *
   ```

   **After**:
   ```
   https://your-frontend-url.vercel.app
   ```

5. Click **"Save Changes"**
6. Render will **redeploy automatically** (~2 minutes)

### 4.2 Test Complete Flow

1. Open your Vercel URL: `https://your-project.vercel.app`
2. Chat interface should load
3. Try asking: **"What events are happening?"**
4. You should see AI response with events!

**✅ If it works, congratulations! Your app is live! 🎉**

---

## 🧪 Testing Your Deployment

### Test 1: Frontend Loads
- Open `https://your-project.vercel.app`
- Should see chat interface with welcome message
- All tabs (Chat, Events, Facilities, Bookings) should work

### Test 2: Backend API
- Open `https://your-backend.onrender.com/docs`
- Should see FastAPI documentation

### Test 3: Chat Functionality
- Type: "What events are happening?"
- Should get response with event list

### Test 4: Events Tab
- Click "Events" tab
- Should see 3 sample events

### Test 5: Booking Flow
- Type: "Book Seminar Hall A for March 30 at 3 PM"
- Should get confirmation prompt
- Type: "confirm"
- Should create booking

---

## ⚠️ Common Issues & Solutions

### Issue 1: Backend Returns 500 Error

**Cause**: MongoDB connection failed

**Solution**:
1. Check MONGO_URL in Render environment variables
2. Ensure password is correct (no special characters encoded)
3. Verify MongoDB Atlas network access allows 0.0.0.0/0
4. Check Render logs for detailed error

### Issue 2: Frontend Can't Connect to Backend

**Cause**: CORS or wrong API URL

**Solutions**:
1. Verify `REACT_APP_BACKEND_URL` in Vercel
2. Check CORS_ORIGINS in Render includes your Vercel URL
3. Open browser console (F12) for detailed errors
4. Ensure backend URL doesn't have `/api` at end

### Issue 3: "Cannot read property of undefined"

**Cause**: API response format mismatch

**Solution**:
1. Check backend is returning correct JSON format
2. Test API endpoint directly: `https://your-backend.onrender.com/api/events`
3. Ensure sample data is seeded

### Issue 4: First Load Very Slow

**Cause**: Render free tier spins down after inactivity

**Solution**:
- This is expected on free tier
- First request takes 30-60 seconds
- Subsequent requests are fast
- Consider paid tier for production

### Issue 5: LLM API Errors

**Cause**: Invalid or expired Emergent LLM key

**Solution**:
1. Verify EMERGENT_LLM_KEY in Render
2. Check key is valid
3. Ensure key has sufficient credits
4. Check Render logs for specific API errors

---

## 🔐 Security Best Practices

### 1. Restrict CORS
Update `CORS_ORIGINS` to only your Vercel domain:
```
https://your-app.vercel.app
```

### 2. Restrict MongoDB Network Access
In MongoDB Atlas:
1. Go to Network Access
2. Remove `0.0.0.0/0`
3. Add specific Render IP ranges

### 3. Environment Variables
- Never commit `.env` files
- Use Render/Vercel environment variable management
- Rotate API keys regularly

### 4. Rate Limiting
Consider adding rate limiting middleware to backend

---

## 💰 Cost Breakdown

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Vercel** | ✅ Free | 100GB bandwidth/month |
| **Render** | ✅ Free | 750 hours/month, sleeps after 15min |
| **MongoDB Atlas** | ✅ Free | 512MB storage |
| **Emergent LLM** | 💳 Pay per use | Token-based pricing |

**Total**: $0/month (except LLM usage)

---

## 📈 Upgrading to Production

When ready for production:

### Render Upgrade ($7/month)
- No sleep time
- Persistent service
- Better performance

### MongoDB Atlas Upgrade ($9/month)
- 2GB storage
- Better performance
- Automated backups

### Vercel Pro ($20/month)
- More bandwidth
- Custom domains
- Better analytics

---

## 🔄 Continuous Deployment

Both Vercel and Render support automatic deployments:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Automatic Deployment**
   - Vercel: Rebuilds frontend automatically
   - Render: Redeploys backend automatically

3. **Monitor Deployments**
   - Vercel dashboard shows build logs
   - Render dashboard shows deployment status

---

## 📊 Monitoring & Logs

### Render Logs
1. Go to Render dashboard
2. Select your service
3. Click **"Logs"**
4. Real-time logs appear

Useful for debugging:
- API errors
- Database connection issues
- LLM API errors

### Vercel Logs
1. Go to Vercel dashboard
2. Select your project
3. Click **"Deployments"**
4. Click on a deployment
5. View **"Runtime Logs"**

---

## 🎉 Success Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created
- [ ] Connection string obtained
- [ ] Backend deployed on Render
- [ ] Backend URL working (`/api/` endpoint responds)
- [ ] Frontend deployed on Vercel
- [ ] Frontend loads in browser
- [ ] Chat functionality works
- [ ] Events tab shows data
- [ ] Facilities tab shows data
- [ ] Booking flow works end-to-end
- [ ] CORS updated with Vercel URL
- [ ] All environment variables set

---

## 📱 Sharing Your Project

Your live URLs:

**Frontend (User-facing)**:
```
https://your-project.vercel.app
```

**Backend API**:
```
https://your-backend.onrender.com
```

**API Documentation**:
```
https://your-backend.onrender.com/docs
```

Share the frontend URL for:
- Resume/Portfolio
- Assignment submission
- Client demos
- Interviews

---

## 🆘 Getting Help

### Render Issues
- Docs: https://render.com/docs
- Community: https://community.render.com

### Vercel Issues
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

### MongoDB Issues
- Docs: https://docs.mongodb.com
- Community: https://community.mongodb.com

---

## 📝 Quick Reference

### Useful Commands

**Check Backend Status:**
```bash
curl https://your-backend.onrender.com/api/
```

**Test Events API:**
```bash
curl https://your-backend.onrender.com/api/events
```

**View Frontend Environment:**
Open browser console:
```javascript
console.log(process.env.REACT_APP_BACKEND_URL)
```

### Important URLs

- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **MongoDB Atlas**: https://cloud.mongodb.com

---

## 🚀 You're Live!

Congratulations! Your College Campus AI Agent is now deployed and accessible worldwide!

**Next Steps:**
1. Test all features thoroughly
2. Share your live URL
3. Add to your resume/portfolio
4. Monitor usage and logs
5. Collect feedback
6. Iterate and improve

**Your project is now production-ready! 🎊**
