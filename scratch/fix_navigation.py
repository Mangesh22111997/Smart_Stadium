
import os
import re

pages_dir = r"g:\Mangesh\Hack2Skill_Google_Challenge_copilot\streamlit_app\pages"

replacements = {
    r"pages/1_Login\.py": "pages/00_login.py",
    r"pages/2_Signup\.py": "pages/01_signup.py",
    r"pages/01_home\.py": "pages/02_home.py",
    r"pages/02_events\.py": "pages/03_events.py",
    r"pages/03_bookings\.py": "pages/04_bookings.py",
    r"pages/04_maps\.py": "pages/05_maps.py",
    r"pages/05_food\.py": "pages/06_food.py",
    r"pages/06_event_booking\.py": "pages/07_event_booking.py",
    r"pages/8_Notifications\.py": "pages/08_notifications.py",
    r"pages/9_Admin_Dashboard\.py": "pages/09_admin_dashboard.py",
    r"pages/13_Security_Login\.py": "pages/13_security_login.py",
    r"pages/14_Security_Dashboard\.py": "pages/14_security_dashboard.py"
}

for filename in os.listdir(pages_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(pages_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filename}")
