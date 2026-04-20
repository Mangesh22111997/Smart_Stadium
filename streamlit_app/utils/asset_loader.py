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
def render_accessible_image(
    image_data: str,
    alt_text: str,
    caption: str = None,
    width: str = "100%"
) -> None:
    """
    Render an image with proper alt text for screen readers.
    Uses HTML img tag so alt attribute is honoured.

    Args:
        image_data: Base64 encoded image string
        alt_text:   Descriptive text for screen readers (required)
        caption:    Optional visible caption below the image
        width:      CSS width value
    """
    import streamlit as st
    caption_html = f"<figcaption style='font-size:13px;color:#666;margin-top:4px;'>{caption}</figcaption>" if caption else ""
    st.markdown(f"""
    <figure role="img" aria-label="{alt_text}" style="margin:0;">
        <img src="data:image/png;base64,{image_data}"
             alt="{alt_text}"
             style="width:{width};border-radius:8px;"
             loading="lazy" />
        {caption_html}
    </figure>
    """, unsafe_allow_html=True)
