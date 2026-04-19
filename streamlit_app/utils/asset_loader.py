
import streamlit as st
import base64
import os

@st.cache_data(ttl=3600, show_spinner=False)
def get_local_asset(asset_path: str) -> str:
    """
    Load a local image asset and return its base64 string.
    
    Args:
        asset_path: The absolute or relative path to the asset file.
        
    Returns:
        Base64 string of the asset or None if not found
    """
    if os.path.exists(asset_path):
        try:
            with open(asset_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            print(f"Error reading local asset {asset_path}: {e}")
            
    return None

def get_background_base64() -> str:
    """
    Helper to get the main background image from the local path.
    """
    # Hardcoded path as per user request
    path = r"G:\Mangesh\Hack2Skill_Google_Challenge_copilot\bkg_image\Gemini_Generated_Image_ylkdo2ylkdo2ylkd.png"
    return get_local_asset(path)
