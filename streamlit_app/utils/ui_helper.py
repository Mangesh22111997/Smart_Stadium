import streamlit as st
from utils.asset_loader import get_background_base64

def add_background_image():
    """
    Apply a premium semi-transparent background image to the Streamlit app.
    Fetches the image from Firebase via asset_loader.
    """
    img_base64 = get_background_base64()
    
    if img_base64:
        bg_style = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        
        .main {{
            background: transparent;
        }}
        
        /* Premium card styling for containers */
        .stContainer, .content-card, .event-card, .header-container {{
            background: rgba(255, 255, 255, 0.96) !important;
            border-radius: 15px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
            backdrop-filter: blur(15px);
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        /* Accessible typography */
        h1, h2, h3, h4, p, span, label {{
            color: #1a1a1a !important;
            text-shadow: none !important;
        }}
        
        /* High-contrast focus ring for keyboard navigation */
        button:focus, input:focus, select:focus {{
            outline: 3px solid #6366f1 !important;
            outline-offset: 2px;
        }}
        </style>
        """
        st.markdown(bg_style, unsafe_allow_html=True)
    else:
        # Fallback premium gradient
        st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        </style>
        """, unsafe_allow_html=True)
