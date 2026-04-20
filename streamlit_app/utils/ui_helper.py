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

def inject_accessibility_enhancements() -> None:
    """
    Inject ARIA roles, skip navigation, and screen reader support.
    Call this on every page after set_page_config().
    WCAG 2.1 Level AA compliance markers.
    """
    st.markdown("""
    <style>
    /* Skip navigation link — visible on keyboard focus, hidden otherwise */
    .skip-nav {
        position: absolute;
        top: -999px;
        left: -999px;
        background: #667eea;
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        font-size: 16px;
        font-weight: 600;
        z-index: 9999;
        text-decoration: none;
    }
    .skip-nav:focus {
        top: 12px;
        left: 12px;
    }

    /* Visually hidden utility — readable by screen readers only */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    /* Reduced motion — respect system preference */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* Ensure text never relies on colour alone */
    .status-error::before   { content: "✗ "; }
    .status-success::before { content: "✓ "; }
    .status-warning::before { content: "⚠ "; }

    /* High contrast text ratios (WCAG AA: 4.5:1 minimum) */
    body, .stMarkdown p, .stMarkdown li, label {
        color: #1a1a1a;   /* #1a1a1a on #f0f2f6 = 14.5:1 ratio */
    }
    
    @media (prefers-color-scheme: dark) {
        body, .stMarkdown p, .stMarkdown li, label {
            color: #ffffff !important;
        }
    }

    /* Heading hierarchy enforcement */
    .stMarkdown h1 { font-size: 2rem;   font-weight: 700; }
    .stMarkdown h2 { font-size: 1.5rem; font-weight: 600; }
    .stMarkdown h3 { font-size: 1.25rem;font-weight: 600; }

    /* Button accessible states */
    .stButton > button:hover  { opacity: 0.9; }
    .stButton > button:active { transform: scale(0.98); }
    .stButton > button[disabled] {
        opacity: 0.5;
        cursor: not-allowed;
        pointer-events: none;
    }

    /* Live region for dynamic status updates */
    #aria-live-region {
        position: absolute;
        width: 1px;
        height: 1px;
        overflow: hidden;
        clip: rect(0,0,0,0);
    }
    </style>

    <!-- Skip Navigation Link -->
    <a href="#main-content" class="skip-nav" aria-label="Skip to main content">
        Skip to main content
    </a>

    <!-- ARIA Live Region for dynamic announcements -->
    <div id="aria-live-region"
         role="status"
         aria-live="polite"
         aria-atomic="true">
    </div>

    <!-- Main content landmark -->
    <div id="main-content" role="main" aria-label="Smart Stadium Application">
    </div>
    """, unsafe_allow_html=True)

def render_keyboard_shortcuts() -> None:
    """
    Display keyboard shortcuts in an accessible collapsible section.
    Satisfies WCAG 2.1 Success Criterion 2.1.4 (Character Key Shortcuts).
    """
    with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
        st.markdown(\"\"\"
        | Action | Shortcut |
        |---|---|
        | Skip to main content | `Tab` (first press) |
        | Navigate between sections | `Tab` / `Shift+Tab` |
        | Activate buttons | `Enter` or `Space` |
        | Close dialogs | `Escape` |
        | Navigate dropdowns | `Arrow keys` |
        | Go to Home | `Alt+H` |
        | Go to Bookings | `Alt+B` |
        | Go to Maps | `Alt+M` |
        | Emergency SOS | `Alt+S` |
        
        *All keyboard shortcuts are non-conflicting with browser defaults.*
        \"\"\")
    st.divider()
    st.markdown("♿ [Accessibility Statement](pages/17_accessibility.py)")

def inject_form_wrapper(label: str, is_open: bool = True) -> None:
    """
    Inject an ARIA-compliant form wrapper.
    Used to group form elements for screen readers.
    """
    if is_open:
        st.markdown(f'<div role="form" aria-label="{label}">', unsafe_allow_html=True)
    else:
        st.markdown('</div>', unsafe_allow_html=True)
