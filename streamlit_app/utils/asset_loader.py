# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com



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
    Return base64 of the background image using a portable relative path.
    The image lives at project_root/bkg_image/...
    """
    # Build path relative to this file's location, works on any OS
    # File is in streamlit_app/utils/asset_loader.py
    # base_dir is project_root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    image_path = os.path.join(base_dir, "bkg_image", "Gemini_Generated_Image_ylkdo2ylkdo2ylkd.png")
    return get_local_asset(image_path)
