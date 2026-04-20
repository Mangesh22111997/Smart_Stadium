# ============================================================
# Smart Stadium — Cloud Run Deployment Script (Fixed)
# Run from project root: .\deploy.ps1
# Prereqs:
#   gcloud auth login
#   gcloud config set project smart-stadium-system-db
#   gcloud artifacts repositories create stadium-repo --repository-format=docker --location=asia-south1
# ============================================================

$PROJECT_ID  = "smart-stadium-system-db"
$REGION      = "asia-south1"
$REPO_NAME   = "stadium-repo"
$REGISTRY    = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"

$FIREBASE_VARS = @(
    "FIREBASE_API_KEY=AIzaSyCcanmGKxtXCawn0EML0bpL6LgmI1p2CiE",
    "FIREBASE_AUTH_DOMAIN=smart-stadium-system-db.firebaseapp.com",
    "FIREBASE_DATABASE_URL=https://smart-stadium-system-db-default-rtdb.asia-southeast1.firebasedatabase.app",
    "FIREBASE_PROJECT_ID=smart-stadium-system-db",
    "FIREBASE_STORAGE_BUCKET=smart-stadium-system-db.firebasestorage.app",
    "FIREBASE_MESSAGING_SENDER_ID=771554077981",
    "FIREBASE_APP_ID=1:771554077981:web:2b627c9f72edb53a5245f4",
    "SECRET_KEY=stadium-secret-key-hackathon-2026-premium-safety",
    "DEBUG=false"
) -join ","

Write-Host ""
Write-Host "=========================================="
Write-Host "  Smart Stadium Cloud Run Deployment"
Write-Host "  Project: $PROJECT_ID  |  Region: $REGION"
Write-Host "=========================================="

# ── STEP 1: Build backend image via cloudbuild.backend.yaml ─────────────────
Write-Host "`n[1/4] Building backend Docker image..."
& gcloud builds submit `
    --config cloudbuild.backend.yaml `
    --project $PROJECT_ID `
    .
if ($LASTEXITCODE -ne 0) { Write-Error "Backend build failed"; exit 1 }

# ── STEP 2: Deploy backend ──────────────────────────────────────────────────
Write-Host "`n[2/4] Deploying backend to Cloud Run..."
& gcloud run deploy stadium-backend `
    --image "${REGISTRY}/stadium-backend:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 1 `
    --timeout 300 `
    --concurrency 80 `
    --min-instances 0 `
    --max-instances 5 `
    --port 8080 `
    --set-env-vars $FIREBASE_VARS
if ($LASTEXITCODE -ne 0) { Write-Error "Backend deployment failed"; exit 1 }

$BACKEND_URL = (& gcloud run services describe stadium-backend `
    --platform managed --region $REGION --format "value(status.url)").Trim()
Write-Host "Backend URL: $BACKEND_URL"

# ── STEP 3: Build frontend image ─────────────────────────────────────────────
Write-Host "`n[3/4] Building frontend Docker image..."
& gcloud builds submit `
    --config cloudbuild.frontend.yaml `
    --project $PROJECT_ID `
    .
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend build failed"; exit 1 }

# ── STEP 4: Deploy frontend ──────────────────────────────────────────────────
Write-Host "`n[4/4] Deploying frontend to Cloud Run..."
& gcloud run deploy stadium-frontend `
    --image "${REGISTRY}/stadium-frontend:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --concurrency 80 `
    --min-instances 0 `
    --max-instances 3 `
    --port 8080 `
    --set-env-vars "API_BASE_URL=${BACKEND_URL}"
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend deployment failed"; exit 1 }

$FRONTEND_URL = (& gcloud run services describe stadium-frontend `
    --platform managed --region $REGION --format "value(status.url)").Trim()

# ── Patch backend CORS with the live frontend URL ─────────────────────────
Write-Host "`nPatching backend CORS with frontend URL..."
& gcloud run services update stadium-backend `
    --platform managed `
    --region $REGION `
    --update-env-vars "FRONTEND_URL=${FRONTEND_URL}"

Write-Host ""
Write-Host "=========================================="
Write-Host "  DEPLOYMENT COMPLETE"
Write-Host "  Frontend : $FRONTEND_URL"
Write-Host "  Backend  : $BACKEND_URL"
Write-Host "  API Docs : ${BACKEND_URL}/docs"
Write-Host "=========================================="
