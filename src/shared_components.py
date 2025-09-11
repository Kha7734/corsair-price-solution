import streamlit as st


@st.fragment
def sidebar_info_fragment():
    """Shared sidebar fragment for all pages"""
    # Data validation statistics
    session_table = st.session_state.session_table

    if session_table.is_validation_completed():
        validated_data = session_table.get_validated_data()
        if validated_data is not None:
            valid_count = len(
                validated_data[validated_data["IsValid"] == True])
            invalid_count = len(
                validated_data[validated_data["IsValid"] == False])
            total_count = len(validated_data)
            accuracy = valid_count / total_count * 100 if total_count > 0 else 0

            st.header("📊 Data Quality")

            st.metric("✅ Valid Rows", valid_count)
            st.metric("❌ Invalid Rows", invalid_count)
            st.metric("📊 Total Rows", total_count)
            st.metric("🎯 Quality Score", f"{accuracy:.1f}%")

            # Show selected country if available
            selected_country = session_table.get_selected_country()
            if selected_country:
                st.markdown("**🌍 Selected country:**")
                st.write(selected_country)

            # Show confirmation status
            if session_table.is_confirmation_completed():
                st.success("✅ Data Confirmed")
            else:
                st.info("⏳ Awaiting Confirmation")

def init_sidebar():
    """Initialize sidebar for any page - call this in every page"""
    # Initialize session table if not exists
    if "session_table" not in st.session_state:
        from src.data_handler import SessionTable
        st.session_state.session_table = SessionTable()

    # Render sidebar content
    with st.sidebar:
        sidebar_info_fragment()
