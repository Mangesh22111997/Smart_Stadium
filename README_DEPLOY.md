
# 🚀 Smart Stadium - Cloud Run Deployment Guide

This guide explains how to deploy your Smart Stadium system to Google Cloud Run using the provided scripts.

## 1. Prerequisites
Ensure you have the following installed and configured:
*   [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
*   Initialized gcloud: `gcloud init`
*   Enabled APIs: `Cloud Run`, `Artifact Registry`, `Cloud Build`

## 2. One-Time Setup
Create the repository in Artifact Registry:
```powershell
gcloud artifacts repositories create stadium-repo --repository-format=docker --location=asia-south1
```

## 3. Deploying
Simply run the deployment script in PowerShell:
```powershell
.\deploy.ps1
```

## 4. Secret Management
The script currently passes some environment variables via CLI. For the most secure production setup, you should:
1.  Go to the **Cloud Run Console**.
2.  Select your service.
3.  Go to **Edit & Deploy New Revision**.
4.  Add your `GOOGLE_APPLICATION_CREDENTIALS` as a **Secret** using **Secret Manager**.

## 5. Cleaning Up
If you want to stop the services to save on potential (though unlikely) costs:
```powershell
gcloud run services delete stadium-backend --region=asia-south1
gcloud run services delete stadium-frontend --region=asia-south1
```
