
import streamlit as st
from utils.asset_loader import get_asset_from_db

def show_success_animation(message: str = "Success!"):
    """
    Display a branded success animation with a custom GIF from the database.
    
    Args:
        message: The success message to display below the animation.
    """
    gif_base64 = get_asset_from_db("loading_gif_base64")
    if gif_base64:
        st.markdown(
            f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">'
            f'<img src="data:image/gif;base64,{gif_base64}" width="150" alt="Success Animation">'
            f'<h3 style="color: #28a745; margin-top: 10px;">{message}</h3>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.success(message)
