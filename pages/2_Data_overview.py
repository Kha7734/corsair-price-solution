import streamlit as st
from src.data_handler import SessionTable
from src.data_display import data_overview_section
from src.country_selection import country_selection_section, confirm_selection_section
from src.shared_components import init_sidebar

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
        st.markdown("### Confirm Selection")
        confirm_selection_section(selected_country)

    # Show confirmation status
    if session_table.is_confirmation_completed():
        confirmed_data = session_table.get_confirmed_data()
        selected_country = session_table.get_selected_country()

        st.success("✅ Data confirmed and ready for analysis!")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Confirmed Rows", len(confirmed_data))
        with col2:
            st.metric("🌍 country", selected_country)


if __name__ == "__main__":
    main()
