"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""


import streamlit as st

def show_success_animation(message: str = "Success!"):
    """
    Display a success message. 
    Simplified as per user request (removing custom GIF loader).
    
    Args:
        message: The success message to display.
    """
    st.success(message)
    st.balloons()  # Adding a simple built-in Streamlit animation for premium feel
