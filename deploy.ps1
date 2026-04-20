
# Google Cloud Run Deployment Script for Smart Stadium
# Clean version without special characters to avoid PowerShell encoding issues

$PROJECT_ID = "smart-stadium-system-db"
$REGION = "asia-south1"
$REPO_NAME = "stadium-repo"

Write-Host "Starting Smart Stadium Deployment..."

# 1. Build and Push Backend
Write-Host "Building Backend Image..."
Copy-Item Dockerfile.backend Dockerfile
& gcloud builds submit --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/stadium-backend:latest" .
$BUILD_CODE = $LASTEXITCODE
Remove-Item Dockerfile
if ($BUILD_CODE -ne 0) { Write-Error "Backend Build Failed"; exit $BUILD_CODE }

Write-Host "Deploying Backend to Cloud Run..."
# Added --memory 2Gi to ensure ML models and dependencies have enough headroom
& gcloud run deploy stadium-backend `
    --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/stadium-backend:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 2Gi `
    --set-env-vars "FIREBASE_API_KEY=AIzaSyCcanmGKxtXCawn0EML0bpL6LgmI1p2CiE,FIREBASE_AUTH_DOMAIN=smart-stadium-system-db.firebaseapp.com,FIREBASE_DATABASE_URL=https://smart-stadium-system-db-default-rtdb.asia-southeast1.firebasedatabase.app,FIREBASE_PROJECT_ID=smart-stadium-system-db,FIREBASE_STORAGE_BUCKET=smart-stadium-system-db.firebasestorage.app,FIREBASE_MESSAGING_SENDER_ID=771554077981,FIREBASE_APP_ID=1:771554077981:web:2b627c9f72edb53a5245f4,SECRET_KEY=stadium-secret-key-hackathon-2026-premium-safety"
if ($LASTEXITCODE -ne 0) { Write-Error "Backend Deployment Failed"; exit $LASTEXITCODE }

# Get Backend URL
$BACKEND_URL = & gcloud run services describe stadium-backend --platform managed --region $REGION --format 'value(status.url)'
Write-Host "Backend deployed at: $BACKEND_URL"

# 2. Build and Push Frontend
Write-Host "Building Frontend Image..."
Copy-Item Dockerfile.frontend Dockerfile
& gcloud builds submit --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/stadium-frontend:latest" .
$BUILD_CODE = $LASTEXITCODE
Remove-Item Dockerfile
if ($BUILD_CODE -ne 0) { Write-Error "Frontend Build Failed"; exit $BUILD_CODE }

Write-Host "Deploying Frontend to Cloud Run..."
& gcloud run deploy stadium-frontend `
    --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/stadium-frontend:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 1Gi `
    --set-env-vars "API_BASE_URL=$BACKEND_URL"
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend Deployment Failed"; exit $LASTEXITCODE }

$FRONTEND_URL = & gcloud run services describe stadium-frontend --platform managed --region $REGION --format 'value(status.url)'
Write-Host "DEPLOYMENT COMPLETE!"
Write-Host "Frontend: $FRONTEND_URL"
Write-Host "Backend:  $BACKEND_URL"
