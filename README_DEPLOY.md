# 🚀 Smart Stadium — Google Cloud Run Deployment

Professional serverless deployment guide for the Hack2Skill Smart Stadium System.

## 📋 One-Time Infrastructure Setup
1. **Login & Project Set**:
   ```powershell
   gcloud auth login
   gcloud config set project smart-stadium-system-db
   ```
2. **Enable Required APIs**:
   ```powershell
   gcloud services enable run.googleapis.com \
                          artifactregistry.googleapis.com \
                          cloudbuild.googleapis.com
   ```
3. **Create Artifact Repository**:
   ```powershell
   gcloud artifacts repositories create stadium-repo \
       --repository-format=docker \
       --location=asia-south1 \
       --description="Smart Stadium Docker Repository"
   ```

## 🚢 Quick Deploy
The system uses a 4-step automated deployment process (Backend Build → Backend Deploy → Frontend Build → Frontend Deploy).

Run the fixed PowerShell script:
```powershell
.\deploy.ps1
```

## 🛠️ Architecture Overview
* **Backend**: FastAPI running on Python 3.12 (2Gi RAM, 1 vCPU).
* **Frontend**: Streamlit Dashboard (1Gi RAM, 1 vCPU).
* **Communication**: Frontend calls Backend via `API_BASE_URL` env var.
* **Security**: Backend CORS is restricted to the specific Frontend Cloud Run URL.

## 🧪 Local Development
To run both services locally for testing:
* **Windows**: Run `.\startup.bat`
* **Linux/Mac**: Run `./startup.sh`

Both scripts will automatically:
1. Create/activate a virtual environment.
2. Install dependencies from both backend and frontend requirement files.
3. Launch the Backend (8000) and Frontend (8501) in separate processes.
