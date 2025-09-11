import streamlit as st
from src.data_handler import validate_data, prepare_display_data


def data_overview_section():
    """Main data overview section with consistent modal handling"""
    session_table = st.session_state.session_table

    # Initialize modal states
    from .modals import initialize_modal_states, show_confirmation_modal, show_processing_modal, show_success_modal
    initialize_modal_states()

    # Show modals in sequence
    if st.session_state.show_confirmation_modal:
        show_confirmation_modal()
        return

    if st.session_state.show_processing_modal:
        show_processing_modal()
        return

    if st.session_state.show_success_modal:
        show_success_modal()
        return

    # Regular data overview content
    st.header("📊 Data Overview")

    original_data = session_table.get_original_data()
    selected_country = session_table.get_selected_country()

    if original_data is not None:
        # Control bar
        _render_control_bar(selected_country, session_table)

        # Display data table
        _display_data_table(session_table)


def _render_control_bar(selected_country, session_table):
    """Render the control bar with validation and view options"""
    col1, col2, col3, col4 = st.columns([2, 2, 1.5, 0.5])

    with col1:
        if st.button("Validate Data", type="secondary", icon="🔍"):
            session_table.log_message(
                f"Validation button clicked for country: {selected_country}")
            with st.spinner(f"Validating entire dataset for {selected_country}..."):
                validate_data()
            st.rerun()

    with col2:
        if session_table.is_validation_completed():
            view_filter = st.selectbox(
                "View:",
                ["All Rows", "Valid Only", "Invalid Only"],
                key="view_filter",
                label_visibility="collapsed",
            )
        else:
            view_filter = "All Rows"
            st.selectbox(
                "View:",
                ["Preview Mode"],
                disabled=True,
                key="preview_mode",
                label_visibility="collapsed",
            )

    with col3:
        if session_table.is_validation_completed():
            row_limit = st.selectbox(
                "Show:",
                [10, 25, 50, 100, "All"],
                key="row_limit",
                label_visibility="collapsed",
            )
        else:
            row_limit = st.selectbox(
                "Preview:",
                [5, 10, 20, "All"],
                key="preview_limit",
                label_visibility="collapsed",
            )

    with col4:
        if st.button("🗑️", help="Clear all data"):
            session_table.log_message("Clear data button clicked")
            session_table.clear_all()
            st.rerun()


def _display_data_table(session_table):
    """Display the data table with appropriate filtering"""
    try:
        view_filter = st.session_state.get("view_filter", "All Rows")
        row_limit = st.session_state.get("row_limit", 10)

        display_df = prepare_display_data(view_filter, row_limit)
        if display_df is not None:
            st.dataframe(display_df)

            selected_country = session_table.get_selected_country()
            if session_table.is_validation_completed():
                st.caption(
                    f"Showing {len(display_df)} rows from {view_filter.lower()} for {selected_country}")
            else:
                st.caption(
                    f"Showing preview of first {len(display_df)} rows for {selected_country}")
        else:
            st.warning("No data to display")
    except Exception as e:
        error_msg = f"Error displaying data: {str(e)}"
        session_table.log_message(error_msg, "ERROR")
        st.error(f"❌ {error_msg}")


def show_debug_log():
    """Display debug log in an expandable section"""
    session_table = st.session_state.session_table
    logs = session_table.get_logs()

    if logs:
        with st.expander("🔍 Debug Log", expanded=False):
            for log_entry in logs:
                if "ERROR" in log_entry:
                    st.error(log_entry)
                elif "WARNING" in log_entry:
                    st.warning(log_entry)
                else:
                    st.text(log_entry)

            if st.button("🗑️ Clear Log", key="clear_log_btn"):
                st.session_state.session_data["validation_log"] = []
                st.rerun()
