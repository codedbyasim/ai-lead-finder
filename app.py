"""
Streamlit UI for AI Lead Finder System
Main application interface
"""

import streamlit as st
import logging
from typing import List
from pipeline import LeadPipeline, Lead
from exporter import CSVExporter
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Lead Finder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_header():
    """Render application header"""
    st.title("🤖 AI Freelance Lead Finder")
    st.markdown("**Find potential clients who need your AI/Dev services**")
    st.markdown("---")


def render_input_form() -> dict:
    """Render input form and return user inputs"""
    st.subheader("📋 Lead Generation Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Niche selection
        niche = st.selectbox(
            "Select Business Niche",
            options=[
                "Real Estate",
                "Private Schools & Academies",
                "Clinics & Hospitals",
                "E-commerce Stores",
                "Software Houses & Digital Agencies"
            ],
            help="Choose the type of businesses you want to target"
        )
        
        # City input
        city = st.text_input(
            "Enter City",
            value="Islamabad",
            help="Target city for lead generation (e.g., Islamabad, Lahore, Karachi)"
        )
    
    with col2:
        # Service selection
        services = st.multiselect(
            "Select Services to Offer",
            options=[
                "AI Chatbot",
                "Web Scraping",
                "Automation",
                "Dashboard Development",
                "Appointment Booking System",
                "Customer Support Bot"
            ],
            default=["AI Chatbot"],
            help="Services you want to offer to potential clients"
        )
        
        # Lead count
        lead_count = st.slider(
            "Number of Leads",
            min_value=10,
            max_value=100,
            value=20,
            step=5,
            help="How many leads do you want to generate?"
        )
    
    # Language preference
    language = st.radio(
        "Pitch Message Language",
        options=["Urdu", "English"],
        horizontal=True,
        help="Language for personalized pitch messages"
    )
    
    return {
        'niche': niche,
        'city': city,
        'services': services,
        'lead_count': lead_count,
        'language': language
    }


def render_progress(status: str, percent: float):
    """Render progress bar and status"""
    progress_bar = st.progress(percent / 100)
    status_text = st.empty()
    status_text.text(status)


def render_results(leads: List[Lead], language: str):
    """Render lead results"""
    if not leads:
        st.warning("No leads found. Try different search criteria.")
        return
    
    st.success(f"✅ Found {len(leads)} leads!")
    
    # Check if rule-based scoring was used
    rule_based_count = sum(
        1 for lead in leads
        if lead.problem_detected and "rule_based" not in lead.problem_detected
        and lead.lead_score > 0
    )
    ai_scored = sum(1 for lead in leads if lead.pitch_message and len(lead.pitch_message) > 60)
    if ai_scored < len(leads) // 2:
        st.warning(
            "⚠️ AIML API quota exceeded — leads scored using rule-based method. "
            "Get a new API key at [aimlapi.com](https://aimlapi.com/app/keys) and update AIML_API_KEY in .env"
        )
    
    # Summary statistics
    exporter = CSVExporter()
    stats = exporter.get_summary_stats(leads)
    
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", stats['total_leads'])
        st.metric("High Score", stats['high_score_leads'], delta="Priority")
    
    with col2:
        st.metric("Medium Score", stats['medium_score_leads'])
        st.metric("Low Score", stats['low_score_leads'])
    
    with col3:
        st.metric("Avg Score", f"{stats['average_score']}/100")
        st.metric("With Email", stats['leads_with_email'])
    
    with col4:
        st.metric("With Phone", stats['leads_with_phone'])
        st.metric("With WhatsApp", stats['leads_with_whatsapp'])
    
    st.markdown("---")
    
    # Categorized leads
    st.subheader("🎯 Lead Details")
    
    # Tabs for different score categories
    tab1, tab2, tab3 = st.tabs(["🔥 High Score", "⚡ Medium Score", "📋 All Leads"])
    
    with tab1:
        high_leads = [lead for lead in leads if lead.score_category == 'High']
        render_lead_table(high_leads, language, tab_prefix="high")
    
    with tab2:
        medium_leads = [lead for lead in leads if lead.score_category == 'Medium']
        render_lead_table(medium_leads, language, tab_prefix="med")
    
    with tab3:
        render_lead_table(leads, language, tab_prefix="all")


def render_lead_table(leads: List[Lead], language: str, tab_prefix: str = "t"):
    """Render table of leads"""
    if not leads:
        st.info("No leads in this category")
        return
    
    for i, lead in enumerate(leads, 1):
        with st.expander(f"{i}. {lead.business_name} - Score: {lead.lead_score}/100 ({lead.score_category})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Website:** [{lead.website_url}]({lead.website_url})")
                st.markdown(f"**Niche:** {lead.niche} | **City:** {lead.city}")
                st.markdown(f"**Problem:** {lead.problem_detected}")
                st.markdown(f"**Suggested Service:** {lead.suggested_service}")
                
                if lead.technologies:
                    st.markdown(f"**Technologies:** {', '.join(lead.technologies)}")
                
                # Pitch message — tab_prefix + index = always unique across all tabs
                st.markdown("**📧 Pitch Message:**")
                st.text_area(
                    "Copy this message",
                    value=lead.pitch_message,
                    height=100,
                    key=f"pitch_{tab_prefix}_{i}"
                )
            
            with col2:
                st.markdown("**📞 Contact Info:**")
                if lead.email:
                    st.markdown(f"✉️ {lead.email}")
                if lead.phone:
                    st.markdown(f"📱 {lead.phone}")
                if lead.whatsapp:
                    st.markdown(f"💬 WhatsApp: {lead.whatsapp}")
                
                st.markdown(f"**Chatbot:** {'✅ Yes' if lead.has_chatbot else '❌ No'}")


def render_download_button(leads: List[Lead]):
    """Render CSV download button"""
    if not leads:
        return
    
    st.markdown("---")
    st.subheader("📥 Export Leads")
    
    try:
        exporter = CSVExporter()
        csv_filename = exporter.export_to_csv(leads)
        
        # Read CSV for download
        with open(csv_filename, 'rb') as f:
            csv_data = f.read()
        
        st.download_button(
            label="📥 Download CSV File",
            data=csv_data,
            file_name=csv_filename,
            mime='text/csv',
            help="Download all leads as CSV file"
        )
        
        st.success(f"✅ CSV file ready: {csv_filename}")
        
    except Exception as e:
        st.error(f"Error creating CSV: {e}")


def render_error(message: str):
    """Render error message"""
    st.error(f"❌ Error: {message}")


def render_sidebar():
    """Render sidebar with info"""
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        **AI Lead Finder** helps freelancers find potential clients who need:
        - AI Chatbots
        - Web Scraping
        - Automation
        - Dashboards
        - And more!
        
        ### How it works:
        1. Select your target niche and city
        2. Choose services you offer
        3. System searches and analyzes businesses
        4. Get scored leads with pitch messages
        5. Download CSV and start outreach!
        
        ### Target Niches:
        - Real Estate Agencies
        - Schools & Academies
        - Clinics & Hospitals
        - E-commerce Stores
        - Software Houses
        """)
        
        st.markdown("---")
        st.markdown("**Powered by:**")
        st.markdown("- Bright Data APIs")
        st.markdown("- Google Gemini AI")
        st.markdown("- Python + Streamlit")
        
        st.markdown("---")
        st.caption("© 2025 AI Lead Finder")


def main():
    """Main application"""
    # Render sidebar
    render_sidebar()
    
    # Render header
    render_header()
    
    # Check configuration
    try:
        config.validate()
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {e}")
        st.info("Please set up your API keys in the .env file")
        st.code("""
# Create a .env file with:
BRIGHT_DATA_API_KEY=your_bright_data_key_here
BRIGHT_DATA_SERP_ZONE=serp_api2
BRIGHT_DATA_UNLOCKER_ZONE=web_unlocker1
AIML_API_KEY=your_aiml_api_key_here
AIML_MODEL=anthropic/claude-opus-4-8
        """)
        return
    
    # Render input form
    inputs = render_input_form()
    
    # Generate leads button
    st.markdown("---")
    if st.button("🔍 Find Leads", type="primary", use_container_width=True):
        # Validate inputs
        if not inputs['services']:
            st.warning("Please select at least one service")
            return
        
        # Initialize session state for results
        if 'leads' not in st.session_state:
            st.session_state.leads = None
        
        # Progress container
        progress_container = st.container()
        
        with progress_container:
            st.subheader("🔄 Processing...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(message, percent):
                """Update progress"""
                progress_bar.progress(percent / 100)
                status_text.text(message)
            
            try:
                # Run pipeline
                pipeline = LeadPipeline()
                service = ', '.join(inputs['services'])
                
                leads = pipeline.run(
                    niche=inputs['niche'],
                    city=inputs['city'],
                    service=service,
                    count=inputs['lead_count'],
                    progress_callback=progress_callback
                )
                
                # Store in session state
                st.session_state.leads = leads
                st.session_state.language = inputs['language']
                
                # Clear progress
                progress_container.empty()
                
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
                render_error(str(e))
                return
    
    # Display results if available
    if 'leads' in st.session_state and st.session_state.leads:
        render_results(st.session_state.leads, st.session_state.get('language', 'Urdu'))
        render_download_button(st.session_state.leads)


if __name__ == "__main__":
    main()
