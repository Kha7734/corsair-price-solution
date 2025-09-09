import streamlit as st
from src.data_handler import SessionTable
from src.ui_components import (
    upload_file_section, 
    data_overview_section, 
    country_selection_section,
    confirm_selection_section
)
from src.config import COUNTRY_LIST

# Set page config
st.set_page_config(
    page_title="Price Intelligence Solution",
    page_icon="💰",
    layout="wide"
)

# Initialize session table
session_table = SessionTable()

def create_global_container():
    """Create a global 80% width container"""
    left_spacer, main_content, right_spacer = st.columns([0.1, 0.8, 0.1])
    return main_content

def main():
    with create_global_container():
        st.title("💰 Price Intelligence Solution")
        
        # Upload section
        upload_file_section()
        
        # Data overview section (only show if data is loaded)
        if session_table.get_original_data() is not None:
            data_overview_section()
            
            # Country selection section
            selected_country = country_selection_section()
            confirm_selection_section(selected_country)
        else:
            st.markdown("---")
            st.info("👆 Please upload a file to get started")

if __name__ == "__main__":
    main()
