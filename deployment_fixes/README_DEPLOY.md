# 🚀 Smart Stadium — Cloud Run Deployment Guide

## Architecture

```
Cloud Run: stadium-backend  (FastAPI · port 8080 · asia-south1)
Cloud Run: stadium-frontend (Streamlit · port 8080 · asia-south1)
Firebase Realtime Database  (asia-southeast1)
Google Cloud Logging        (automatic via google-cloud-logging)
```

---

## Prerequisites

```powershell
# 1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
# 2. Authenticate
gcloud auth login
gcloud config set project smart-stadium-system-db

# 3. Enable required APIs (one-time)
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable logging.googleapis.com

# 4. Create Artifact Registry repo (one-time)
gcloud artifacts repositories create stadium-repo `
    --repository-format=docker `
    --location=asia-south1 `
    --description="Smart Stadium Docker images"

# 5. Authorise Docker to push to Artifact Registry (one-time)
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

---

## Deploy (every time)

```powershell
.\deploy.ps1
```

The script:
1. Builds the **backend** image using `cloudbuild.backend.yaml` → `Dockerfile.backend`
2. Deploys `stadium-backend` to Cloud Run with all Firebase env vars
3. Builds the **frontend** image using `cloudbuild.frontend.yaml` → `Dockerfile.frontend`
4. Deploys `stadium-frontend` with `API_BASE_URL` pointing to the live backend
5. Patches `FRONTEND_URL` on the backend so CORS allows the frontend origin

At the end you will see:
```
Frontend : https://stadium-frontend-xxx-el.a.run.app
Backend  : https://stadium-backend-xxx-el.a.run.app
API Docs : https://stadium-backend-xxx-el.a.run.app/docs
```

---

## How PORT works on Cloud Run

Cloud Run **always injects `PORT=8080`** into the container.

- `Dockerfile.backend` CMD: `uvicorn ... --port ${PORT:-8080}` — reads `$PORT`
- `Dockerfile.frontend` CMD: `streamlit run ... --server.port=${PORT:-8080}` — reads `$PORT`
- `config.toml` does **not** set `port` — it would override the CMD value

Never hardcode port `8000` or `8501` in Dockerfiles or config.toml.

---

## Environment Variables

### Backend (set in deploy.ps1 via --set-env-vars)

| Variable | Description |
|---|---|
| `FIREBASE_API_KEY` | Firebase Web API key |
| `FIREBASE_AUTH_DOMAIN` | Firebase auth domain |
| `FIREBASE_DATABASE_URL` | Realtime Database URL |
| `FIREBASE_PROJECT_ID` | GCP project ID |
| `FIREBASE_STORAGE_BUCKET` | Storage bucket name |
| `FIREBASE_MESSAGING_SENDER_ID` | FCM sender ID |
| `FIREBASE_APP_ID` | Firebase App ID |
| `SECRET_KEY` | JWT signing secret (min 32 chars) |
| `FRONTEND_URL` | Auto-set by deploy.ps1 after frontend deploys |
| `DEBUG` | `false` in production |

### Frontend (set in deploy.ps1)

| Variable | Description |
|---|---|
| `API_BASE_URL` | Full Cloud Run URL of the backend service |

---

## Local Development

```bash
# Linux / Mac
./startup.sh

# Windows
startup.bat
```

Local URLs:
- Backend:  http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

---

## Troubleshooting

### Container failed to start and listen on PORT

**Cause**: One of:
- Dockerfile CMD hardcodes `--port 8000` instead of `--port ${PORT:-8080}`
- `config.toml` has `port = 8501` overriding the CMD value
- A required env var is missing causing the app to exit before binding

**Fix**: Use the fixed Dockerfiles and `config.toml` from this repo.

### CORS errors in browser (frontend can't reach backend)

**Cause**: Backend `ALLOWED_ORIGINS` only lists `localhost`. The Cloud Run frontend URL is different.

**Fix**: The fixed `app/main.py` uses `allow_origin_regex=r"https://.*\.run\.app"` and also reads `FRONTEND_URL` env var.

### Firebase connection error at startup

**Cause**: `FIREBASE_DATABASE_URL` or `FIREBASE_API_KEY` env var missing.

**Fix**: Verify all vars are set in deploy.ps1 `$FIREBASE_VARS`. Check Cloud Run service → Edit & Deploy → Variables.

### `EnvironmentError: Required environment variable SECRET_KEY is not set`

**Cause**: `SECRET_KEY` missing from `--set-env-vars`.

**Fix**: Add `SECRET_KEY=your-secret` to the `$FIREBASE_VARS` array in `deploy.ps1`.

### Build fails: Dockerfile not found

**Cause**: Old `deploy.ps1` used `Copy-Item Dockerfile.backend Dockerfile` and `gcloud builds submit --tag`. This is fragile.

**Fix**: The new `deploy.ps1` uses `--config cloudbuild.backend.yaml` which references the Dockerfile explicitly.

---

## Tear Down

```powershell
gcloud run services delete stadium-backend  --region=asia-south1 --quiet
gcloud run services delete stadium-frontend --region=asia-south1 --quiet
```
