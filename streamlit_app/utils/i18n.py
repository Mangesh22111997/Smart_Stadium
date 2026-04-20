
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
    },
    "mr": {
        "welcome": "स्मार्ट स्टेडियममध्ये आपले स्वागत आहे",
        "book_tickets": "तिकीट बुक करा",
        "browse_food": "फूड मेनू पहा",
        "my_bookings": "माझ्या बुकिंग",
        "stadium_maps": "इंटरएक्टिव्ह नकाशे",
        "gate_assigned": "तुमचा नियुक्त गेट **{gate}** आहे",
        "booking_confirmed": "🎉 बुकिंग यशस्वी झाली!",
        "order_placed": "✅ ऑर्डर यशस्वीरित्या दिला!",
        "need_parking": "पार्किंग हवे आहे?",
        "commute_mode": "तुम्ही कसे प्रवास कराल?",
        "confirm_pay": "पुष्टी करा आणि पेमेंट करा",
        "logout": "🚪 लॉगआउट",
        "history": "तुमच्या बुकिंगचा इतिहास",
        "parking_enabled": "{mode} साठी पार्किंग सक्षम आहे"
    }
}

def t(key: str, **kwargs) -> str:
    """
    Retrieve a localized string based on the current session language.
    """
    lang = st.session_state.get("lang", "en")
    template = STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))
    return template.format(**kwargs)

def language_selector():
    """Display a language selection widget in the sidebar."""
    with st.sidebar:
        st.divider()
        lang_options = ["en", "hi", "mr"]
        lang_names = {
            "en": "English",
            "hi": "हिन्दी (Hindi)",
            "mr": "मराठी (Marathi)"
        }
        
        current_lang = st.session_state.get("lang", "en")
        if current_lang not in lang_options:
            current_lang = "en"
            
        lang = st.selectbox(
            "🌐 Language / भाषा / भाषा",
            options=lang_options,
            format_func=lambda x: lang_names[x],
            index=lang_options.index(current_lang),
            key="lang_selector"
        )
        
        if lang != st.session_state.get("lang"):
            st.session_state.lang = lang
            st.rerun()
