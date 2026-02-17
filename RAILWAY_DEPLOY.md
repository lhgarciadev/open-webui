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

| Variable           | Description                                       | Example           |
| ------------------ | ------------------------------------------------- | ----------------- |
| `OPENAI_API_KEY`   | Your OpenAI API key                               | `sk-proj-xxxx...` |
| `WEBUI_SECRET_KEY` | JWT secret (generate with `openssl rand -hex 32`) | `a1b2c3d4...`     |

### Optional

| Variable              | Default                     | Description                                     |
| --------------------- | --------------------------- | ----------------------------------------------- |
| `WEBUI_NAME`          | `Cognitia`                  | Brand name displayed in UI                      |
| `OPENAI_API_BASE_URL` | `https://api.openai.com/v1` | OpenAI API endpoint                             |
| `ENABLE_SIGNUP`       | `true`                      | Allow new user registration                     |
| `DEFAULT_USER_ROLE`   | `pending`                   | Role for new users (`pending`, `user`, `admin`) |
| `PORT`                | `8080`                      | Server port (Railway sets this automatically)   |

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

## MCPO Service (MCP Tools)

MCPO is a satellite service that exposes MCP (Model Context Protocol) servers as OpenAPI endpoints, enabling Cognitia to use tools like PowerPoint generation.

### Deploy MCPO Service

1. In your Railway project, click **New Service** → **GitHub Repo**
2. Select the same repository
3. Go to **Settings** → **Source**:
   - **Root Directory**: Leave empty
   - **Config File Path**: `/mcpo-service/railway.json`
4. Set **PORT** variable to `8000`
5. Deploy

### Connect MCPO to Cognitia

1. In Cognitia, go to **Settings** → **Tools** → **Tool Servers**
2. Add new server:
   - **URL**: `https://mcpo-production-xxxx.up.railway.app`
   - Or use internal: `http://mcpo.railway.internal:8000`
3. Save and the PowerPoint tools will be available

### MCPO Files

- `Dockerfile.mcpo` - MCPO container with PowerPoint MCP server
- `mcpo-service/config.json` - MCP server configuration
- `mcpo-service/railway.json` - Railway config for MCPO service

---

## Files Created for Railway

- `Dockerfile.railway` - Optimized slim build for Cognitia
- `Dockerfile.mcpo` - MCPO service with PowerPoint tools
- `railway.json` - Railway configuration for main app
- `mcpo-service/` - MCPO service configuration
- `RAILWAY_DEPLOY.md` - This guide

---

## Local LLM Service (Hugging Face Spaces)

As of 2026-02-15, local LLM models run on Hugging Face Spaces with ZeroGPU instead of Railway.

### Current Architecture

| Service      | Platform  | URL                                        |
| ------------ | --------- | ------------------------------------------ |
| Cognitia App | Railway   | https://cognitia-production.up.railway.app |
| Local LLMs   | HF Spaces | https://Juansquiroga-cognitia-llm.hf.space |

### Available Local Models

| Model    | Parameters | Use Case                           |
| -------- | ---------- | ---------------------------------- |
| Phi-3    | 3.8B       | Fast general tasks                 |
| Qwen 2.5 | 7B         | High quality, excellent in Spanish |
| SmolLM2  | 1.7B       | Ultra-fast, efficient              |
| Mistral  | 7B         | Reasoning and code                 |

### Hardware

- **GPU**: NVIDIA H200 via ZeroGPU (~70GB VRAM)
- **Cost**: $0 (free tier) or $9/month (PRO for priority)
- **Daily quota**: 25 minutes (PRO)

### Integration

Local models appear in Cognitia with the `cognitia/` prefix (e.g., `cognitia/SmolLM2`). They show no API costs in the model selector and are identified with a "Local" badge.

### Maintenance

To modify models, edit `app.py` in the HuggingFace Space:
https://huggingface.co/spaces/Juansquiroga/cognitia-llm

### Migration Notes

The previous Railway Ollama service was decommissioned. The `OLLAMA_BASE_URL` and `RAILWAY_SERVICE_OLLAMA_URL` environment variables have been removed from Railway.
