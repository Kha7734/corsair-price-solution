import streamlit as st
import time


def initialize_modal_states():
    """Initialize modal-related session state variables"""
    if 'show_confirmation_modal' not in st.session_state:
        st.session_state.show_confirmation_modal = False
    if 'show_processing_modal' not in st.session_state:
        st.session_state.show_processing_modal = False
    if 'show_success_modal' not in st.session_state:
        st.session_state.show_success_modal = False
    if 'data_push_completed' not in st.session_state:
        st.session_state.data_push_completed = False
    if 'modal_data' not in st.session_state:
        st.session_state.modal_data = {}


@st.dialog("Confirm Data Push")
def show_confirmation_modal():
    """Display initial confirmation modal"""
    country = st.session_state.modal_data.get('country', '')
    row_count = st.session_state.modal_data.get('row_count', 0)

    st.warning(
        f"⚠️ Are you sure you want to push this data for **{country}**?")

    # Show data details
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Rows to Push", row_count)
    with col2:
        st.metric("🌍 Target Country", country)

    st.divider()

    # Button row
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancel", type="tertiary"):
            # Clear modal states
            st.session_state.show_confirmation_modal = False
            st.session_state.modal_data = {}
            st.rerun()

    with col2:
        if st.button("✅ Yes, Push Data", type="tertiary"):
            # Move to processing state
            st.session_state.show_confirmation_modal = False
            st.session_state.show_processing_modal = True
            st.rerun()


@st.dialog("Processing Data Push")
def show_processing_modal():
    """Display processing modal with progress"""
    country = st.session_state.modal_data.get('country', '')
    st.info(f"🔄 **Processing data push for {country}...**")

    # Create progress simulation
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Simulate processing steps
    steps = [
        "Validating data format...",
        "Connecting to server...",
        "Uploading data...",
        "Processing records...",
        "Finalizing push..."
    ]

    for i, step in enumerate(steps):
        status_text.text(step)
        time.sleep(0.4)  # Simulate processing time
        progress_bar.progress((i + 1) / len(steps))

    # Complete processing
    st.session_state.show_processing_modal = False
    st.session_state.show_success_modal = True
    st.session_state.data_push_completed = True

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    st.rerun()


@st.dialog("Data Push Successful")
def show_success_modal():
    """Display success modal after data push completion"""
    country = st.session_state.modal_data.get('country', '')
    row_count = st.session_state.modal_data.get('row_count', 0)

    st.success("🎉 **Data Push Completed Successfully!**")
    st.markdown(
        f"✅ Your data for **{country}** has been pushed and will be reflected in **24 hours** on the dashboard.")

    # Show processing summary
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Records Processed", row_count)
    with col2:
        st.metric("🌍 Country", country)

    # OK button to close modal
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        if st.button("✅ OK", type="secondary", use_container_width=True):
            # Clear all modal states
            st.session_state.show_confirmation_modal = False
            st.session_state.show_processing_modal = False
            st.session_state.show_success_modal = False
            st.session_state.data_push_completed = False
            st.session_state.modal_data = {}

            # Clear all session data
            session_table = st.session_state.session_table
            session_table.clear_all()
            session_table.log_message(
                f"Data push completed for {country} - cleared all data and navigating to Upload page")

            # Navigate to Upload Data page
            st.switch_page("pages/1_Upload_data.py")
