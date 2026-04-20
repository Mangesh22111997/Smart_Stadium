# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Terms and Conditions Page
"""

from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image, inject_accessibility_enhancements, render_keyboard_shortcuts

# Apply Background and Accessibility Enhancements
add_background_image()
inject_accessibility_enhancements()

# Sidebar shortcuts
with st.sidebar:
    render_keyboard_shortcuts()



st.markdown("# 📜 Terms and Conditions")
st.markdown("*Last Updated: April 19, 2026*")

st.divider()

tabs = st.tabs(["Terms & Conditions", "Privacy Policy", "User Agreement"])

with tabs[0]:
    st.markdown("""
    ## Terms and Conditions
    
    ### 1. Acceptance of Terms
    By accessing and using the Smart Stadium System, you accept and agree to be bound by the terms and provision of this agreement.
    
    ### 2. Use License
    Permission is granted to temporarily download one copy of the materials (information or software) on Smart Stadium's website for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:
    - Modify or copy the materials
    - Use the materials for any commercial purpose or for any public display
    - Attempt to decompile or reverse engineer any software contained on the website
    - Remove any copyright or other proprietary notations from the materials
    - Transfer the materials to another person or "mirror" the materials on any other server
    
    ### 3. Disclaimer
    The materials on Smart Stadium's website are provided on an 'as is' basis. Smart Stadium makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
    
    ### 4. Limitations
    In no event shall Smart Stadium or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on Smart Stadium's website, even if Smart Stadium or an authorized representative has been notified orally or in writing of the possibility of such damage.
    
    ### 5. Accuracy of Materials
    The materials appearing on Smart Stadium's website could include technical, typographical, or photographic errors. Smart Stadium does not warrant that any of the materials on its website are accurate, complete, or current.
    
    ### 6. Materials Related to Smart Stadium's Business
    Smart Stadium may revise the materials contained on its website at any time without notice. Smart Stadium does not commit to updating the materials.
    
    ### 7. Links
    Smart Stadium has not reviewed all of the sites linked to its website and is not responsible for the contents of any such linked site. The inclusion of any link does not imply endorsement by Smart Stadium of the site. Use of any such linked website is at the user's own risk.
    
    ### 8. Modifications
    Smart Stadium may revise these terms of service for its website at any time without notice. By using this website, you are agreeing to be bound by the then current version of these terms of service.
    
    ### 9. Governing Law
    These terms and conditions are governed by and construed in accordance with the laws of India, and you irrevocably submit to the exclusive jurisdiction of the courts in that location.
    
    ### 10. User Conduct
    Users agree not to post, upload, or otherwise transmit through the Service any content that:
    - Is unlawful, threatening, abusive, defamatory, obscene, or otherwise objectionable
    - Violates any law, regulation, or third party rights
    - Violates the intellectual property rights of Smart Stadium or any third party
    - Is spam, junk mail, or unsolicited commercial email
    """)

with tabs[1]:
    st.markdown("""
    ## Privacy Policy
    
    ### 1. Information We Collect
    We collect information you provide directly to us, such as:
    - Name, email address, and phone number
    - Payment and billing information
    - Event preferences and booking history
    - Communication preferences
    - Profile information and photos
    
    ### 2. How We Use Your Information
    We use the information we collect to:
    - Provide, maintain, and improve our services
    - Process transactions and send related information
    - Send technical notices and support messages
    - Respond to your comments and questions
    - Send promotional communications (with your consent)
    - Monitor and analyze trends and usage
    - Prevent fraudulent and unauthorized activity
    
    ### 3. Information Sharing
    We do not sell, trade, or rent your personal information to third parties. We may share information with:
    - Service providers who assist in operating our website and conducting our business
    - Entities as required by law or with your consent
    - In the event of merger, acquisition, or asset sale
    
    ### 4. Security
    We take reasonable measures to protect your personal information from unauthorized access, alteration, and destruction. However, no method of transmission over the Internet is 100% secure.
    
    ### 5. Cookies and Tracking
    We use cookies and similar technologies to track activity on our service and store certain information. You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent.
    
    ### 6. Data Retention
    We retain your personal information for as long as your account is active or as needed to provide our services, unless a longer retention period is required by law.
    
    ### 7. Your Privacy Rights
    You have the right to:
    - Access your personal information
    - Correct inaccurate data
    - Request deletion of your data (subject to legal obligations)
    - Opt-out of marketing communications
    """)

with tabs[2]:
    st.markdown("""
    ## User Agreement
    
    ### 1. Eligibility
    You must be at least 18 years of age to use Smart Stadium. By creating an account, you represent and warrant that you are 18 years or older.
    
    ### 2. Account Registration
    When you create an account, you agree to:
    - Provide accurate and complete information
    - Maintain the confidentiality of your password
    - Accept responsibility for all activity that occurs under your account
    - Notify us immediately of any unauthorized use
    
    ### 3. Booking Cancellations
    Cancellation policies may vary by event. Please review the specific cancellation policy for each event before booking.
    
    ### 4. Prohibited Activities
    You agree not to:
    - Resell tickets without authorization
    - Use automated tools to access our service
    - Attempt to gain unauthorized access to our systems
    - Harass, abuse, or harm other users
    - Interfere with the functioning of our service
    
    ### 5. Event Attendance
    By booking an event, you agree to:
    - Arrive at the specified time
    - Follow all venue and event rules
    - Comply with security procedures
    - Not engage in prohibited activities at the venue
    
    ### 6. Liability Waiver
    You assume all risk related to your use of the service and attendance at events. Smart Stadium is not liable for injuries or damages that may occur.
    
    ### 7. Dispute Resolution
    Any disputes shall be resolved through binding arbitration in accordance with the laws of India.
    
    ### 8. Contact Us
    If you have questions about these terms, please contact:
    - Email: support@smartstadium.com
    - Phone: +91-XXX-XXX-XXXX
    - Address: Smart Stadium, India
    """)

st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("← Back to Signup", use_container_width=True):
        st.switch_page("pages/01_signup.py")
with col2:
    st.info("✅ By checking the box on the signup page, you agree to these Terms and Conditions")
