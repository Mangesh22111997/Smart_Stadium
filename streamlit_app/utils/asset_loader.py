
import streamlit as st
import base64
import os

@st.cache_data(ttl=3600, show_spinner=False)
def get_asset_from_db(asset_name: str) -> str:
    """
    Fetch asset base64 from Firebase Realtime Database.
    
    Args:
        asset_name: The name of the asset (e.g., 'background_base64', 'loading_gif_base64')
        
    Returns:
        Base64 string of the asset or None if not found
    """
    try:
        from app.config.firebase_config import get_db_connection
        db = get_db_connection()
        asset = db.child("assets").child(asset_name).get()
        if asset.val():
            return asset.val()
    except Exception as e:
        print(f"Error fetching asset {asset_name} from DB: {e}")
    
    # Local fallback logic
    fallbacks = {
        "background_base64": r"G:\Mangesh\Hack2Skill_Google_Challenge_copilot\bkg_image\Gemini_Generated_Image_ylkdo2ylkdo2ylkd.png",
        "loading_gif_base64": r"G:\Mangesh\Hack2Skill_Google_Challenge_copilot\loading_gif-anime\Interwind@1x-1.0s-200px-200px.gif"
    }
    
    path = fallbacks.get(asset_name)
    if path and os.path.exists(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
            
    return None
