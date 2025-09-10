import streamlit as st
from src.data_handler import SessionTable
from src.shared_components import init_sidebar

# Set page config - must be the first Streamlit command
st.set_page_config(
    page_title="Price Intelligence Solution",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session table
if "session_table" not in st.session_state:
    st.session_state.session_table = SessionTable()



def main():
    init_sidebar()

    st.title("💰 Price Intelligence Solution")
    st.markdown("### Welcome to the Price Intelligence Dashboard")

    # Get session table
    session_table = st.session_state.session_table

    # Display current status
    original_data = session_table.get_original_data()

    if original_data is None:
        st.info("👈 Please use the **Upload Data** page in the sidebar to get started")

        # Add helpful information
        with st.expander("📋 Getting Started", expanded=True):
            st.markdown("""
            **Step 1:** Upload your data file
            - Go to **📁 Upload Data** page
            - Upload a CSV or Excel file with required columns
            
            **Step 2:** Review and validate data  
            - Go to **📊 Data Overview** page
            - Validate your data and select countries
            
            **Required Columns:**
            - Category, Item, Density, MSRP, PROMO, Discount, Start Date, End Date
            
            **Supported Formats:**
            - CSV (.csv), Excel (.xlsx, .xls)
            """)
    else:
        # Show current data status
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📊 Total Rows", len(original_data))

        with col2:
            st.metric("📋 Columns", len(original_data.columns))

        with col3:
            if session_table.is_validation_completed():
                validated_data = session_table.get_validated_data()
                valid_count = len(
                    validated_data[validated_data['IsValid'] == True])
                st.metric("✅ Valid Rows", valid_count)
            else:
                st.metric("🔍 Status", "Not Validated")

        # Show next steps
        st.markdown("### Next Steps")

        if not session_table.is_validation_completed():
            st.info("📊 Go to **Data Overview** to validate your data")
        elif not session_table.is_confirmation_completed():
            st.info("🌍 Go to **Data Overview** to select and confirm countries")
        else:
            st.success("✅ Data is ready for analysis!")

        # Show recent activity
        logs = session_table.get_logs(5)
        if logs:
            with st.expander("🔍 Recent Activity"):
                for log in logs[-5:]:
                    st.text(log)


if __name__ == "__main__":
    main()
