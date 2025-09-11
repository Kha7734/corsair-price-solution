import streamlit as st


def confirm_country_selection(country):
    """Handle country confirmation - trigger initial modal"""
    session_table = st.session_state.session_table

    try:
        # Initialize modal states
        from .modals import initialize_modal_states
        initialize_modal_states()

        session_table.log_message(
            f"Initiating confirmation for country: {country}")

        # Get validated data
        validated_data = session_table.get_validated_data()
        if validated_data is None:
            st.error("❌ No validated data available")
            return

        # Filter for valid data only
        valid_data = validated_data[validated_data["IsValid"] == True].copy()
        if len(valid_data) == 0:
            st.error("❌ No valid rows found in the dataset")
            return

        # Store confirmed data first
        session_table.store_confirmed_data(valid_data, country)

        # Set modal data and show confirmation modal
        st.session_state.modal_data = {
            'country': country,
            'row_count': len(valid_data)
        }

        st.session_state.show_confirmation_modal = True
        session_table.log_message(
            f"Confirmation modal triggered for {country} with {len(valid_data)} rows")
        st.rerun()

    except Exception as e:
        error_msg = f"Error initiating country confirmation: {str(e)}"
        session_table.log_message(error_msg, "ERROR")
        st.error(f"❌ {error_msg}")
