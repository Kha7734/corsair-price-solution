import streamlit as st
from src.data_handler import SessionTable
from src.ui_components import data_overview_section, country_selection_section, confirm_selection_section

# Set page config
st.set_page_config(
    page_title="Data Overview - Price Intelligence", 
    page_icon="📊",
    layout="wide"
)

# Initialize session table if not exists
if "session_table" not in st.session_state:
    st.session_state.session_table = SessionTable()

def main():
    
    # Get session table
    session_table = st.session_state.session_table
    original_data = session_table.get_original_data()
    
    if original_data is None:
        st.warning("⚠️ No data found. Please upload a file first.")
        st.info("👈 Go to **📁 Upload Data** page to upload your data file")
        return
    
    # Show data overview section
    data_overview_section()
    
    st.markdown("---")
    
    # Country selection section
    st.header("🌍 Country Selection")
    selected_countries = country_selection_section()
    
    # Confirmation section
    if selected_countries:
        st.markdown("### Confirm Selection")
        confirm_selection_section(selected_countries)
    
    # Show confirmation status
    if session_table.is_confirmation_completed():
        confirmed_data = session_table.get_confirmed_data()
        selected_countries = session_table.get_selected_countries()
        
        st.success("✅ Data confirmed and ready for analysis!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Confirmed Rows", len(confirmed_data))
        with col2:
            st.metric("🌍 Countries", ", ".join(selected_countries))

if __name__ == "__main__":
    main()