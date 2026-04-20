# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Accessibility Statement — WCAG 2.1 Level AA compliance documentation
"""

import streamlit as st
st.set_page_config(
    page_title="Accessibility - Smart Stadium",
    page_icon="♿",
    layout="wide"
)

from utils.ui_helper import add_background_image, inject_accessibility_enhancements, render_keyboard_shortcuts, inject_main_content_start, inject_main_content_end
from utils.i18n import language_selector

# Language selection
language_selector()

# Apply Background and Accessibility Enhancements
add_background_image()
inject_accessibility_enhancements()

# Sidebar shortcuts
with st.sidebar:
    render_keyboard_shortcuts()

st.markdown("# ♿ Accessibility Statement")
st.markdown("*Smart Stadium System — WCAG 2.1 Level AA Compliance*")
st.divider()
inject_main_content_start()

st.markdown("""
## Our Commitment

Smart Stadium System is committed to ensuring digital accessibility for people with
disabilities. We continually improve the user experience for everyone and apply the
relevant accessibility standards.

## Conformance Status

This application aims to conform to the **Web Content Accessibility Guidelines (WCAG) 2.1
Level AA**. The guidelines explain how to make web content more accessible to people
with disabilities.

## Technical Specifications

The accessibility of Smart Stadium relies on the following technologies:
- **HTML5** semantic structure
- **WAI-ARIA** (Accessible Rich Internet Applications) attributes
- **CSS3** with reduced-motion support
- **Python / Streamlit** accessible component library

## Accessibility Features Implemented

### Navigation
- ♿ Skip navigation link at top of every page (visible on keyboard focus)
- ⌨️ Full keyboard navigation support throughout the application
- 📍 Consistent navigation structure across all pages
- 🏷️ Descriptive page titles for each section

### Visual Design
- 🎨 Colour contrast ratios meet WCAG AA minimum (4.5:1 for text, 3:1 for UI components)
- ↔️ No information conveyed by colour alone — icons and labels accompany all colour indicators
- 🔍 Text resizable up to 200% without loss of content or functionality
- 🌓 Full dark mode support via `prefers-color-scheme` media query

### Assistive Technology
- 📖 Screen reader compatible — all images have descriptive alt text
- 📢 ARIA live regions announce dynamic content changes (gate updates, order status)
- 🏷️ All form inputs have associated visible labels
- ❌ Error messages are programmatically associated with their form fields

### Motor Accessibility
- 👆 All interactive elements meet the 44×44px minimum touch target size (WCAG 2.5.5)
- 🖱️ No functionality requires precise mouse movement or hover-only interactions
- ⏱️ No time limits on any user actions
- 🎬 All animations respect the `prefers-reduced-motion` system setting

### Language Support
- 🌐 Available in English (en), Hindi (हिन्दी), and Marathi (मराठी)
- 📝 Language attribute is set programmatically on all content

## Known Limitations

The following areas have known accessibility limitations we are actively working to improve:
- Third-party map embeds (Google Maps iframes) have limited screen reader support
- Some chart visualisations in the admin dashboard require descriptive text alternatives

## Feedback

We welcome feedback on the accessibility of Smart Stadium. If you experience any barriers:
- 📧 Email: accessibility@smartstadium.app
- 🔗 Submit an issue via the Settings page

We aim to respond to accessibility feedback within 2 business days.

## Standards Applied

| Standard | Level | Status |
|---|---|---|
| WCAG 2.1 — Perceivable | AA | Implemented |
| WCAG 2.1 — Operable | AA | Implemented |
| WCAG 2.1 — Understandable | AA | Implemented |
| WCAG 2.1 — Robust | AA | In Progress |
| Section 508 (US) | — | Compatible |
| EN 301 549 (EU) | — | Compatible |
""")

st.divider()
inject_main_content_start()
st.caption("Last reviewed: April 2026 | Smart Stadium System v1.0")

