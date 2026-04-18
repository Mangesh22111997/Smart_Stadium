# Smart Stadium System - Frontend Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Backend running on http://127.0.0.1:8000
- Streamlit installed

### Installation

```bash
# Navigate to project directory
cd g:\Mangesh\Hack2Skill_Google_Challenge_copilot

# Install dependencies (if not already installed)
pip install streamlit streamlit-option-menu plotly

# Make sure backend is running (in separate terminal)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Running the Frontend

```bash
# Run Streamlit app
streamlit run frontend.py

# The app will open at http://localhost:8501
```

## 📱 User Interfaces

### 1. **CUSTOMER-FACING UI** 👤

Accessible for ticket holders to track their event journey.

#### Login
- **Email**: Any email address
- **Ticket ID**: Event ticket number

#### Features Available:
- **My Journey**: View booking details, gate assignment, entry timeline
- **Gate Info**: Real-time gate capacity, wait times, alternatives
- **Food Ordering**: Browse menu, place orders, track preparation
- **Notifications**: View system notifications and updates
- **Alerts**: Emergency notifications and safety information

#### Use Cases:
```
✓ "Where is my assigned gate?"
✓ "How long until I can enter?"
✓ "What food is available?"
✓ "How crowded is my gate?"
✓ "Is there an emergency?"
```

---

### 2. **ADMIN/STAFF UI** 👮

Restricted access for stadium staff and management.

#### Login
- **Staff ID**: STAFF-001, STAFF-002, etc.
- **Password**: `staff123` (demo access)

#### Features Available:

##### Dashboard 📊
- System KPIs (total users, active gates, avg wait time)
- Real-time crowd flow visualization
- System health metrics
- Hourly trends

##### Crowd Monitor 👥
- Live gate utilization (color-coded: 🟢 low, 🟡 medium, 🔴 high)
- Quick redistribution triggers
- Bottleneck identification

##### User Management 👥
- View active users and their gates
- Reassign users to different gates
- Bulk operations (evacuation, alerts)
- Search and filter

##### Emergency Management 🚨
- Active emergency status
- Quick announcement system
- Emergency zone management
- Response tracking

##### Analytics 📊
- Daily metrics and KPIs
- Department performance
- Trend analysis
- Historical data

##### Settings ⚙️
- Configure alert thresholds
- System parameters
- Security settings
- API configuration

## 🎨 Interface Features

### Common Elements
- **Status Indicators**: 🟢 Green (OK), 🟡 Yellow (Warning), 🔴 Red (Alert)
- **Real-time Updates**: Auto-refresh data
- **Responsive Design**: Works on desktop and tablet
- **Dark/Light Mode**: Toggle via Streamlit theme settings

### Data Visualizations
- Gate utilization bar charts
- Crowd flow line charts
- User distribution pie charts
- Timeline views
- Performance gauges

## 🔑 Demo Credentials

### Customer Demo
```
Email: john.doe@example.com
Ticket ID: TICKET-123456
```

### Admin Demo
```
Staff ID: STAFF-001
Password: staff123
```

## 🌐 API Integration

The frontend connects to the backend API at `http://127.0.0.1:8000`

### Endpoints Used:
- `GET /health` - Check backend status
- `GET /api/v1/orchestration/system-health` - System status
- `POST /api/v1/orchestration/user-journey/register-and-book` - User registration
- `GET /api/v1/orchestration/user-journey/{id}` - Journey status
- `POST /api/v1/orchestration/redistribute-users` - Load balancing
- `POST /api/v1/orchestration/food-ordering/{id}` - Food orders
- `POST /api/v1/orchestration/evacuation` - Emergency evacuation
- `POST /api/v1/orchestration/emergency-sos/{id}` - Emergency SOS
- `GET /api/v1/orchestration/event-log` - Event history
- `GET /api/v1/orchestration/journey-analytics` - Analytics
- `POST /api/v1/orchestration/sync-all-systems` - System sync

## 📊 Key Workflows

### Customer Workflow
```
1. Login with email & ticket
2. View journey status
3. Check gate assignment
4. See wait time
5. Order food (optional)
6. Proceed to gate
```

### Admin Workflow
```
1. Login with staff credentials
2. Monitor dashboard
3. Check for overcrowding
4. Trigger redistribution if needed
5. Handle emergencies
6. Review analytics
```

## 🛠️ Troubleshooting

### Backend Not Responding
```
Error: "Backend Server Unavailable"
Solution: 
  1. Check backend is running on port 8000
  2. Run: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  3. Refresh browser
```

### Page Not Loading
```
Error: "Connection error"
Solution:
  1. Ensure both backend and Streamlit are running
  2. Check firewall settings
  3. Try clearing browser cache
  4. Restart Streamlit: Press 'R' in terminal
```

### Authentication Issues
```
Customer Login:
  - Email can be any format (demo mode)
  - Ticket ID is just an identifier (demo mode)

Admin Login:
  - Staff ID: STAFF-001 (or any STAFF-XXX)
  - Password: staff123 (hardcoded for demo)
```

## 🔐 Security Notes

**Development/Demo Mode:**
- Simplified authentication for testing
- No encryption on demo credentials
- Use only in dev environment

**Production Recommendations:**
- Implement OAuth2 / JWT authentication
- Encrypt all API communications
- Use HTTPS instead of HTTP
- Implement role-based access control (RBAC)
- Add API rate limiting
- Secure password hashing

## 📈 Performance

### Expected Load Times:
- Page load: < 2 seconds
- Real-time updates: Every 5-10 seconds
- Chart generation: < 1 second
- API calls: < 500ms average

### Optimization Tips:
- Use `@st.cache_data` for repeated queries
- Implement polling instead of live updates
- Compress data transfers
- Use session state for client-side caching

## 🎯 Feature Roadmap

### Phase 1 (Current) ✓
- Basic UI layout
- Customer dashboard
- Admin dashboard
- API integration

### Phase 2 (Next)
- Real authentication system
- Database backend
- Live data streaming
- Email notifications

### Phase 3 (Future)
- Mobile app
- Advanced analytics
- ML-based predictions
- Multi-language support

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check backend logs
4. Verify all services are running

## 📝 File Structure

```
frontend.py              # Main Streamlit app
api_utils.py            # API utility functions
FRONTEND_GUIDE.md       # This file
startup.bat             # Windows startup script
startup.sh              # Linux/Mac startup script
```

## 🚀 Batch Startup (Easy)

**Windows:**
```bash
Double-click: startup.bat
```

**Linux/Mac:**
```bash
bash startup.sh
```

This will start both backend and frontend automatically.
