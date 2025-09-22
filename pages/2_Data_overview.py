import streamlit as st
from src.data_handler import SessionTable
from src.data_display import data_overview_section
from src.country_selection import country_selection_section, confirm_selection_section
from src.shared_components import init_sidebar
from src.snowflake_handler import upload_dataframe_to_snowflake

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
    # Init sidebar
    init_sidebar()

    # Get session table
    session_table = st.session_state.session_table
    original_data = session_table.get_original_data()

    if original_data is None:
        st.warning("⚠️ No data found. Please upload a file first.")

        if st.button("📊 Upload Data Page", width="stretch"):
            st.switch_page("pages/1_Upload_data.py")

        return

    # Show data overview section
    data_overview_section()

    # Country selection section
    st.header("🌍 Country Selection")
    selected_country = country_selection_section()
    

    # Confirmation section
    if selected_country:
        # st.header("Confirm Selection")
        confirm_selection_section(selected_country)

if __name__ == "__main__":
    main()
