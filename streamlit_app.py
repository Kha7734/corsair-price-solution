import streamlit as st
from src.data_handler import SessionTable
from src.ui_components import (
    upload_file_section,
    data_overview_section,
    country_selection_section,
    confirm_selection_section
)
from src.tab_manager import TabManager
from src.config import COUNTRY_LIST

# Set page config
st.set_page_config(
    page_title="Price Intelligence Solution",
    page_icon="💰",
    layout="wide"
)

# Initialize session table and tab manager
session_table = SessionTable()
tab_manager = TabManager(session_table)

def main():
    # Render left panel with tabs (this will handle auto-switching)
    tab_manager.render_left_panel()
    
    # Main content area
    st.title("💰 Price Intelligence Solution")
    
    # Get current tab
    current_tab = tab_manager.get_current_tab()
    
    # Render content based on selected tab
    if current_tab == "upload":
        render_upload_tab()
    elif current_tab == "overview":
        render_overview_tab()

def render_upload_tab():
    """Render the Upload Data tab content"""
    st.header("📁 Upload Your Data")
    
    # Upload section
    upload_file_section()
    
    # Show instructions if no data
    if session_table.get_original_data() is None:
        st.markdown("---")
        st.info("👆 Please upload a CSV or Excel file to get started")
        
        # Add helpful information
        with st.expander("📋 File Requirements", expanded=True):
            st.markdown("""
            **Required Columns:**
            - ProductID, ItemID, ActualPrice, PromoPrice, StartDate, EndDate
            
            **Supported Formats:**
            - CSV (.csv), Excel (.xlsx, .xls)
            """)

def render_overview_tab():
    """Render the Data Overview tab content"""
    # Data overview section
    data_overview_section()
    
    # Country selection section
    selected_country = country_selection_section()
    confirm_selection_section(selected_country)

if __name__ == "__main__":
    main()