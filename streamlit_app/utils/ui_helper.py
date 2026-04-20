# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com



import streamlit as st
import traceback
from contextlib import contextmanager
from utils.asset_loader import get_background_base64

@contextmanager
def handle_ui_exceptions():
    """
    Context manager to wrap page logic. Catches any unexpected UI exceptions
    and renders a polite, user-friendly error message instead of an ugly traceback.
    """
    try:
        yield
    except Exception as e:
        st.error("⚠️ An unexpected system error occurred while loading this page.")
        st.info("Our team has been notified. Please refresh the page or try again later.")
        print(f"UI Exception Caught: {e}")
        traceback.print_exc()

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
            background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Dark mode overrides */
        @media (prefers-color-scheme: dark) {{
            [data-testid="stAppViewContainer"] {{
                background-image: linear-gradient(rgba(20, 20, 20, 0.85), rgba(20, 20, 20, 0.85)), url("data:image/png;base64,{img_base64}");
            }}
            .stContainer, .content-card, .event-card, .header-container {{
                background: rgba(30, 30, 30, 0.9) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
            }}
            h1, h2, h3, h4, p, span, label {{
                color: #ffffff !important;
            }}
        }}

        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        
        .main {{
            background: transparent;
        }}
        
        /* Premium card styling for containers */
        .stContainer, .content-card, .event-card, .header-container {{
            background: rgba(255, 255, 255, 0.96);
            border-radius: 15px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
            backdrop-filter: blur(15px);
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        /* Accessible typography for headings */
        h1, h2, h3, h4 {{
            text-shadow: none !important;
        }}
        
        /* High-contrast focus ring for keyboard navigation */
        button:focus, input:focus, select:focus {{
            outline: 3px solid #6366f1 !important;
            outline-offset: 2px;
        }}

        /* WCAG 2.5.5: Minimum 48px touch target for mobile stadium use */
        .stButton > button {{
            min-height: 48px !important;
            min-width: 120px !important;
            font-size: 16px !important;
            border-radius: 8px !important;
        }}

        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {{
            min-height: 44px !important;
            font-size: 16px !important;
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
        
        /* Minimum touch target for fallback gradient mode too */
        .stButton > button {
            min-height: 48px !important;
            min-width: 120px !important;
        }
        </style>
        """, unsafe_allow_html=True)
