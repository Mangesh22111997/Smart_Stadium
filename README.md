# 🏟️ Smart Stadium System

A premium, end-to-end event management platform for stadiums, featuring real-time booking, integrated food ordering, and smart navigation powered by Google Cloud Platform.

## 🚀 Quick Start (GCP Track)

### 1. Prerequisites
- Python 3.9+
- Firebase Project (Realtime Database + Auth)
- Google Maps API Key

### 2. Setup
```bash
# Clone the repository
git clone <repo_url>
cd Smart_Stadium

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Firebase and Google Maps credentials
```

### 3. Run the Application
```bash
# Start the Backend (Port 800)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 800

# Start the Frontend (Port 8501)
streamlit run streamlit_app/app.py
```

## 🔑 Test Credentials
| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@stadium.com` | `Admin@123` |
| **User** | `test@stadium.com` | `Test@123` |

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Database**: Firebase Realtime Database
- **Auth**: Firebase Authentication
- **Maps**: Google Maps Embed API
- **Models**: Pydantic v2

## 📜 Documentation
See [STADIUM_SYSTEM_GUIDE.md](./STADIUM_SYSTEM_GUIDE.md) for a full architectural breakdown and hackathon compliance standards.

---
Built for the **Hack2Skill Google Challenge 2026**.
