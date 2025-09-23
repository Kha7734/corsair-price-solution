import streamlit as st
from src.snowflake_handler import upload_original_data_to_snowflake

def initialize_modal_states():
    """Initialize modal-related session state variables."""
    states = {
        'show_confirmation_modal': False,
        'show_processing_modal': False,
        'show_success_modal': False,
        'show_error_modal': False,  # State for the error modal
        'data_push_completed': False,
        'modal_data': {}
    }
    for key, value in states.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.dialog("Confirm Data Push")
def show_confirmation_modal():
    """Display the initial confirmation modal."""
    country = st.session_state.modal_data.get('country', 'N/A')
    row_count = st.session_state.modal_data.get('row_count', 0)

    st.warning(f"⚠️ Are you sure you want to push this data for **{country}**?")
    
    col1, col2 = st.columns(2)
    col1.metric("📊 Rows to Push", f"{row_count:,}")
    col2.metric("🌍 Country", country)
    st.divider()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("❌ Cancel", width="stretch"):
            st.session_state.show_confirmation_modal = False
            st.rerun()

    with col2:
        if st.button("✅ Push Data", type="primary", width="stretch"):
            st.session_state.show_confirmation_modal = False
            st.session_state.show_processing_modal = True
            st.rerun()

@st.dialog("Processing...")
def show_processing_modal():
    """
    Display the processing modal and perform the upload to Snowflake.
    """
    country = st.session_state.modal_data.get('country', 'N/A')
    st.info(f"🔄 **Processing data push for {country}...**")
    st.write("This process may take a few minutes. Please do not close this window.")
    
    with st.spinner("Connecting and uploading data to Snowflake..."):
        session_table = st.session_state.session_table
        # Call the main upload function
        upload_result = upload_original_data_to_snowflake(session_table)

    # Handle the result
    st.session_state.show_processing_modal = False
    if upload_result["success"]:
        # Save success info for display
        st.session_state.modal_data['final_table_name'] = upload_result['table_name']
        st.session_state.modal_data['rows_uploaded'] = upload_result['rows_uploaded']
        st.session_state.show_success_modal = True
    else:
        # Save error message for display
        st.session_state.modal_data['error_message'] = upload_result['message']
        st.session_state.show_error_modal = True
    
    st.rerun()


@st.dialog("Data Push Successful")
def show_success_modal():
    """Display the success modal after completion."""
    country = st.session_state.modal_data.get('country', 'N/A')
    row_count = st.session_state.modal_data.get('rows_uploaded', 0)
    table_name = st.session_state.modal_data.get('final_table_name', 'N/A')

    st.success("🎉 **Data Push Completed Successfully!**")
    
    st.info(f"Table created: `{table_name}`")

    def clear_and_navigate():
        """Clear all states and navigate to upload page."""
        if hasattr(st.session_state, 'session_table'):
            st.session_state.session_table.clear_all()

    if st.button("✅ OK", type="primary", width="stretch", 
                on_click=clear_and_navigate):
        st.switch_page("pages/1_Upload_data.py")
        st.rerun()



@st.dialog("An Error Occurred")
def show_error_modal():
    """Display a modal when an error occurs."""
    error_message = st.session_state.modal_data.get('error_message', 'An unknown error occurred.')

    st.error("❌ **Data Push Failed!**")
    st.write("An error occurred during the process. Please check the details below and try again.")
    st.code(error_message, language=None)

    # Add an option to go back to the previous page or reset
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Close", key="close_error_modal", width="stretch"):
            st.session_state.show_error_modal = False
            st.session_state.show_processing_modal = False
            if 'processing_started' in st.session_state:
                del st.session_state.processing_started
            

    with col2:
        if st.button("Back to Upload", key="back_to_upload", width="stretch"):
            st.session_state.show_error_modal = False
            st.session_state.show_processing_modal = False
            if 'processing_started' in st.session_state:
                del st.session_state.processing_started
            st.switch_page("pages/1_Upload_data.py")

    st.rerun()
