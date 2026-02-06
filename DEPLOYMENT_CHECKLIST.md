# 🚀 Quick Deployment Checklist

## Pre-Deployment
- [ ] Code pushed to GitHub repository
- [ ] All tests passing locally
- [ ] Environment variables documented

## MongoDB Atlas Setup
- [ ] Created free MongoDB Atlas account
- [ ] Created M0 (free) cluster
- [ ] Created database user with password
- [ ] Set network access to 0.0.0.0/0
- [ ] Obtained connection string
- [ ] Updated connection string with password and database name

## Render Backend Deployment  
- [ ] Created Render account
- [ ] Signed in with GitHub
- [ ] Created new Web Service
- [ ] Connected GitHub repository
- [ ] Set build command: `pip install -r backend/requirements.txt`
- [ ] Set start command: `uvicorn backend.server:app --host 0.0.0.0 --port 10000`
- [ ] Added environment variable: `MONGO_URL`
- [ ] Added environment variable: `DB_NAME=campus_agent`
- [ ] Added environment variable: `EMERGENT_LLM_KEY`
- [ ] Added environment variable: `CORS_ORIGINS=*`
- [ ] Deployment successful
- [ ] Tested: `https://your-backend.onrender.com/api/`
- [ ] Tested: `https://your-backend.onrender.com/docs`
- [ ] Saved backend URL for frontend

## Vercel Frontend Deployment
- [ ] Created Vercel account
- [ ] Signed in with GitHub
- [ ] Imported project from GitHub
- [ ] Set root directory to `frontend`
- [ ] Framework preset: Create React App
- [ ] Added environment variable: `REACT_APP_BACKEND_URL=[Your Render URL]`
- [ ] Deployment successful
- [ ] Frontend loads in browser
- [ ] Saved frontend URL

## Post-Deployment Configuration
- [ ] Updated Render `CORS_ORIGINS` with Vercel URL
- [ ] Waited for Render redeploy (~2 minutes)
- [ ] Tested complete flow:
  - [ ] Chat loads with welcome message
  - [ ] Events tab shows data
  - [ ] Facilities tab shows data
  - [ ] Bookings tab works
  - [ ] Can ask questions and get responses
  - [ ] Can create bookings with confirmation

## Final Testing
- [ ] Test on desktop browser
- [ ] Test on mobile browser  
- [ ] Test all intents (events, facilities, booking)
- [ ] Test booking confirmation flow
- [ ] Check browser console for errors
- [ ] Verify all API calls succeed

## Documentation
- [ ] Updated README with live URLs
- [ ] Saved all credentials securely
- [ ] Documented environment variables
- [ ] Added deployment notes

## Production URLs

**Frontend**: `https://_________________.vercel.app`

**Backend**: `https://_________________.onrender.com`

**API Docs**: `https://_________________.onrender.com/docs`

**MongoDB**: `mongodb+srv://_________________`

---

## Quick Test Commands

**Test Backend Health:**
```bash
curl https://your-backend.onrender.com/api/
```

**Test Events API:**
```bash
curl https://your-backend.onrender.com/api/events
```

**Test Chat API:**
```bash
curl -X POST https://your-backend.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What events are happening?"}'
```

---

## ⚠️ Common Issues

**Issue: Backend returns 500 error**
- Check MongoDB connection string
- Verify credentials are correct
- Check Render logs

**Issue: Frontend can't connect**
- Verify REACT_APP_BACKEND_URL in Vercel
- Check CORS_ORIGINS in Render
- Check browser console for errors

**Issue: First load is slow**
- Normal for Render free tier
- Service spins up from sleep (30-60 seconds)

---

## 🎉 Deployment Complete!

Once all checkboxes are checked, your app is:
- ✅ Live and accessible worldwide
- ✅ Using free cloud services
- ✅ Production-ready
- ✅ Resume/Portfolio ready

Share your frontend URL! 🚀
