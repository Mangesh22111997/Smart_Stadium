
import streamlit as st

# Localized strings for Smart Stadium
STRINGS = {
    "en": {
        "welcome": "Welcome to Smart Stadium",
        "book_tickets": "Book Tickets",
        "browse_food": "Browse Food Menu",
        "my_bookings": "My Bookings",
        "stadium_maps": "Interactive Maps",
        "gate_assigned": "Your assigned gate is **{gate}**",
        "booking_confirmed": "🎉 Booking Confirmed!",
        "order_placed": "✅ Order placed successfully!",
        "need_parking": "Need Parking?",
        "commute_mode": "How will you commute?",
        "confirm_pay": "Confirm & Pay",
        "logout": "🚪 Logout",
        "history": "Your Booking History",
        "parking_enabled": "🅿️ Parking enabled for {mode}"
    },
    "hi": {
        "welcome": "स्मार्ट स्टेडियम में आपका स्वागत है",
        "book_tickets": "टिकट बुक करें",
        "browse_food": "फ़ूड मेनू देखें",
        "my_bookings": "मेरी बुकिंग",
        "stadium_maps": "इंटरएक्टिव मैप्स",
        "gate_assigned": "आपका निर्धारित गेट **{gate}** है",
        "booking_confirmed": "🎉 बुकिंग की पुष्टि हुई!",
        "order_placed": "✅ ऑर्डर सफलतापूर्वक दिया गया!",
        "need_parking": "पार्किंग चाहिए?",
        "commute_mode": "आप कैसे आएंगे?",
        "confirm_pay": "पुष्टि करें और भुगतान करें",
        "logout": "🚪 लॉगआउट",
        "history": "आपकी बुकिंग का इतिहास",
        "parking_enabled": "{mode} के लिए पार्किंग सक्षम है"
    }
}

def t(key: str, **kwargs) -> str:
    """
    Retrieve a localized string based on the current session language.
    
    Args:
        key: The key for the localized string.
        kwargs: Formatting arguments.
        
    Returns:
        The localized and formatted string.
    """
    lang = st.session_state.get("lang", "en")
    template = STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))
    return template.format(**kwargs)

def language_selector():
    """Display a language selection widget in the sidebar."""
    with st.sidebar:
        st.divider()
        lang = st.selectbox(
            "🌐 Language / भाषा",
            options=["en", "hi"],
            format_func=lambda x: "English" if x == "en" else "हिन्दी (Hindi)",
            index=0 if st.session_state.get("lang", "en") == "en" else 1,
            key="lang_selector"
        )
        if lang != st.session_state.get("lang"):
            st.session_state.lang = lang
            st.rerun()
