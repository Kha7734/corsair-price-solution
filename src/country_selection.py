import streamlit as st
from src.config import COUNTRY_LIST


def country_selection_section():
    """Handle country single select dropdown"""
    session_table = st.session_state.session_table

    col1, col2 = st.columns([3, 7])
    with col1:
        # Get current selected country from session (should be a single string now)
        current_country = session_table.get_selected_country()

        # Handle legacy list format or ensure it's a string
        if isinstance(current_country, list):
            current_country = current_country[0] if current_country else ""
        elif current_country is None:
            current_country = ""

        # Ensure current country is valid
        if current_country not in COUNTRY_LIST:
            current_country = ""

        # Create country single select with current value as default
        selected_country = st.selectbox(
            "Select country for analysis:",
            options=COUNTRY_LIST,
            index=COUNTRY_LIST.index(
                current_country) if current_country in COUNTRY_LIST else None,
            key="country_selector",
            help="Choose one country for data processing and analysis"
        )

        # Update session if changed
        if selected_country != current_country:
            session_table.set_selected_country(selected_country)
            session_table.log_message(
                f"Country selection changed to: {selected_country}")

        return selected_country


def confirm_selection_section(selected_country):
    """Handle confirmation section for single country"""
    session_table = st.session_state.session_table

    # Confirm button logic
    is_validation_completed = session_table.is_validation_completed()
    all_data_is_valid = session_table.all_data_is_valid()

    # Button should be disabled if no validation or not all data is valid
    button_disabled = not (
        is_validation_completed and all_data_is_valid) or not selected_country

    # Determine help text based on button state
    if button_disabled:
        if not selected_country:
            help_text = "⚠️ Please select a country"
        elif not is_validation_completed:
            help_text = "⚠️ Please validate the data first before confirming country selection"
        elif not all_data_is_valid:
            help_text = "❌ All data must be valid to proceed. Please fix invalid rows first"
        else:
            help_text = "Button is currently disabled"
    else:
        help_text = f"Confirm data processing for: {selected_country}"

    # Confirm button with single country
    if st.button(
        f"Confirm Selection ({selected_country})" if selected_country else "Confirm Selection",
        disabled=button_disabled,
        help=help_text,
        icon="✅",
        use_container_width=True,
    ):
        from src.data_processing import confirm_country_selection
        confirm_country_selection(selected_country)
