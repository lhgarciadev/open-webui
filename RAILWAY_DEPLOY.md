# Cognitia - Railway Deployment Guide

## Quick Deploy

### Option 1: Deploy from GitHub

1. Fork or push this repo to your GitHub
2. Go to [Railway](https://railway.app)
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your repository
5. Railway will auto-detect the `railway.json` and use `Dockerfile.railway`

### Option 2: Deploy via CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

---

## Environment Variables (Required)

Configure these in Railway Dashboard → Your Project → Variables:

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-xxxx...` |
| `WEBUI_SECRET_KEY` | JWT secret (generate with `openssl rand -hex 32`) | `a1b2c3d4...` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBUI_NAME` | `Cognitia` | Brand name displayed in UI |
| `OPENAI_API_BASE_URL` | `https://api.openai.com/v1` | OpenAI API endpoint |
| `ENABLE_SIGNUP` | `true` | Allow new user registration |
| `DEFAULT_USER_ROLE` | `pending` | Role for new users (`pending`, `user`, `admin`) |
| `PORT` | `8080` | Server port (Railway sets this automatically) |

### Generate Secret Key

```bash
openssl rand -hex 32
```

---

## Railway Dashboard Setup

1. **Go to Variables tab**
2. **Add these variables:**

```
OPENAI_API_KEY=sk-proj-your-key-here
WEBUI_SECRET_KEY=your-generated-secret-key
WEBUI_NAME=Cognitia
ENABLE_SIGNUP=true
DEFAULT_USER_ROLE=pending
```

3. **Click Deploy**

---

## Estimated Costs

Railway Hobby Plan ($5/month):
- **Build**: ~5-10 min first deploy
- **Memory**: ~512MB-1GB runtime
- **Storage**: Uses Railway's ephemeral storage (data resets on redeploy)

### For Persistent Data

Add a Railway PostgreSQL database:

1. **Add Service** → **Database** → **PostgreSQL**
2. Add variable: `DATABASE_URL=${{Postgres.DATABASE_URL}}`

---

## Post-Deployment

1. **Access your app**: Railway provides a URL like `cognitia-production.up.railway.app`
2. **Create admin account**: First user to sign up becomes admin
3. **Configure models**: Go to Settings → Connections → verify OpenAI is connected

---

## Troubleshooting

### Build fails
- Check build logs in Railway dashboard
- Ensure `Dockerfile.railway` exists in repo root

### App crashes on start
- Verify `OPENAI_API_KEY` is set correctly
- Check `WEBUI_SECRET_KEY` is set
- View logs in Railway dashboard

### Models not appearing
- Verify OpenAI API key is valid
- Check Settings → Connections in the app

---

## Custom Domain

1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Configure DNS:
   - CNAME: `your-app.up.railway.app`

---

## Files Created for Railway

- `Dockerfile.railway` - Optimized slim build
- `railway.json` - Railway configuration
- `RAILWAY_DEPLOY.md` - This guide
