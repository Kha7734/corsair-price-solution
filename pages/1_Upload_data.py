import streamlit as st
from src.data_handler import SessionTable
from src.ui_components import upload_file_section
from src.shared_components import init_sidebar

# Set page config
st.set_page_config(
    page_title="Upload Data - Price Intelligence",
    page_icon="📁",
    layout="wide"
)

# Initialize session table if not exists
if "session_table" not in st.session_state:
    st.session_state.session_table = SessionTable()

def main():
    st.title("📁 Upload Data")
    
    # Get session table
    session_table = st.session_state.session_table
    
    # Init sidebar
    init_sidebar()

    # Upload section
    upload_file_section()
    
    # Show current file status
    original_data = session_table.get_original_data()
    
    if original_data is not None:
        st.success("✅ File uploaded successfully!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Rows", len(original_data))
        with col2:
            st.metric("📋 Columns", len(original_data.columns))
        
        # Show data preview
        with st.expander("👁️ Data Preview", expanded=False):
            st.dataframe(original_data.head(10))
        
        # Navigation button instead of info message
        st.markdown("---")
        if st.button("📊 Go to Data Overview", width="stretch"):
            st.switch_page("pages/2_Data_overview.py")

    else:
        st.markdown("---")
        st.info("👆 Please upload a CSV or Excel file to get started")
        
        # Add helpful information
        with st.expander("📋 File Requirements", expanded=True):
            st.markdown("""
            **Required Columns:**
            - Category, Item, Density, MSRP, PROMO, Discount, Start Date, End Date
            
            **Supported Formats:**
            - CSV (.csv), Excel (.xlsx, .xls)
            
            **Data Requirements:**
            - MSRP must be > 0
            - PROMO must be >= 0  
            - Discount should be <= 0
            - Start Date must be before End Date
            - Text fields (Category, Item, Density) cannot be empty
            """)

if __name__ == "__main__":
    main()