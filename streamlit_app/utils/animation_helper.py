# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com



import streamlit as st

def show_success_animation(message: str = "Success!", lang: str = "en") -> None:
    """
    Show a success animation that respects prefers-reduced-motion.
    Provides a screen-reader announcement alongside the visual animation.

    Args:
        message: The success message to display and announce
        lang:    Language code for the announcement
    """
    # Screen reader announcement via ARIA live region
    st.markdown(f"""
    <div role="alert"
         aria-live="assertive"
         aria-atomic="true"
         style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);">
        {message}
    </div>
    """, unsafe_allow_html=True)

    # Visual animation — respects prefers-reduced-motion
    st.markdown(f"""
    <style>
    @keyframes successPop {{
        0%   {{ transform: scale(0.8); opacity: 0; }}
        60%  {{ transform: scale(1.05); opacity: 1; }}
        100% {{ transform: scale(1); opacity: 1; }}
    }}
    @media (prefers-reduced-motion: no-preference) {{
        .success-anim {{ animation: successPop 0.4s ease-out forwards; }}
    }}
    </style>
    <div class="success-anim"
         role="status"
         aria-label="{message}"
         style="text-align:center;padding:24px;background:rgba(16,185,129,0.1);
                border-radius:12px;border:2px solid #10b981;">
        <div style="font-size:48px;" aria-hidden="true">✅</div>
        <h2 style="color:#065f46;margin:8px 0 0 0;">{message}</h2>
    </div>
    """, unsafe_allow_html=True)
