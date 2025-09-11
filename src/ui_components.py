import streamlit as st
import pandas as pd
from src.data_handler import SessionTable, validate_data, prepare_display_data
from src.config import COUNTRY_LIST

def upload_file_section():
    """Handle file upload"""
    # Get session table from session state
    session_table = st.session_state.session_table

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload your promotion data file",
    )

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / 1024 / 1024
        file_info = {"name": uploaded_file.name, "size_mb": file_size_mb}

        session_table.log_message(
            f"File uploaded: {uploaded_file.name} ({file_size_mb:.2f} MB)"
        )

        # Check if this is a new file
        current_file_info = session_table.get_original_data()
        if (
            current_file_info is None
            or st.session_state.session_data["file_info"] is None
            or st.session_state.session_data["file_info"]["name"] != uploaded_file.name
        ):
            loading_msg = (
                "🔄 Processing large file..."
                if file_size_mb > 10
                else "📥 Loading file..."
            )

            with st.spinner(loading_msg):
                try:
                    # Parse file
                    if uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(
                            uploaded_file,
                            low_memory=False if file_size_mb > 5 else True,
                        )
                        session_table.log_message(
                            "CSV file parsed successfully")
                    else:
                        df = pd.read_excel(uploaded_file)
                        session_table.log_message(
                            "Excel file parsed successfully")

                    # Store in session table
                    session_table.store_original_data(df, file_info)
                    session_table.log_message(
                        f"Data loaded: {len(df)} rows, {len(df.columns)} columns"
                    )

                    # Trigger rerun to update UI
                    st.rerun()

                except Exception as e:
                    error_msg = f"File upload error: {str(e)}"
                    session_table.log_message(error_msg, "ERROR")
                    st.error(f"❌ Error: {str(e)}")
                    return None

        return session_table.get_original_data()
    return None

def country_selection_section():
    """Handle country single select dropdown"""
    session_table = st.session_state.session_table

    col1, col2 = st.columns([2, 8])

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
            index=COUNTRY_LIST.index(current_country) if current_country in COUNTRY_LIST else None,
            key="country_selector",
            help="Choose one country for data processing and analysis",
        )

        # Update session if changed
        if selected_country != current_country:
            session_table.set_selected_country(selected_country)
            session_table.log_message(f"Country selection changed to: {selected_country}")

        return selected_country

def confirm_selection_section(selected_country):
    """Handle confirmation section for single country"""
    session_table = st.session_state.session_table
    
    # Confirm button logic
    is_validation_completed = session_table.is_validation_completed()
    all_data_is_valid = session_table.all_data_is_valid()

    # Button should be disabled if no validation or not all data is valid
    button_disabled = not (is_validation_completed and all_data_is_valid) or not selected_country

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

    # Show selected country info
    if selected_country:
        st.info(f"📍 Selected country: **{selected_country}**")

    # Confirm button with single country
    if st.button(
        f"Confirm Selection ({selected_country})" if selected_country else "Confirm Selection",
        disabled=button_disabled,
        help=help_text,
        icon="✅",
        width="stretch",  # Changed from width="stretch"
    ):
        confirm_country_selection(selected_country)

def data_overview_section():
    """Main data overview section"""
    session_table = st.session_state.session_table
    
    st.header("📊 Data Overview")

    original_data = session_table.get_original_data()
    selected_country = session_table.get_selected_country()

    if original_data is not None:
        # Control bar
        col1, col2, col3, col4 = st.columns([2, 2, 1.5, 0.5])

        with col1:
            if st.button("Validate Data", type="secondary", icon="🔍"):
                session_table.log_message(
                    f"Validation button clicked for country: {selected_country}"
                )
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

        # Display data table
        try:
            display_df = prepare_display_data(view_filter, row_limit)
            if display_df is not None:
                st.dataframe(display_df, width="stretch")  # Changed from width="stretch"

                # Show info
                if session_table.is_validation_completed():
                    st.caption(
                        f"Showing {len(display_df)} rows from {view_filter.lower()} for {selected_country}"
                    )
                else:
                    st.caption(
                        f"Showing preview of first {len(display_df)} rows for {selected_country}"
                    )
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

def confirm_country_selection(country):
    """Handle country confirmation and data processing for single country"""
    session_table = st.session_state.session_table
    
    try:
        session_table.log_message(f"Confirming selection for country: {country}")

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

        # Store confirmed data (country should be a single string now)
        session_table.store_confirmed_data(valid_data, country)

        # Log confirmation details
        session_table.log_message(
            f"Confirmed {len(valid_data)} valid rows for country: {country}"
        )

        # Show success message
        st.success(
            f"✅ Successfully confirmed {len(valid_data)} valid rows for country: {country}"
        )

        # Rerun to update UI
        st.rerun()

    except Exception as e:
        error_msg = f"Error confirming country selection: {str(e)}"
        session_table.log_message(error_msg, "ERROR")
        st.error(f"❌ {error_msg}")

@st.fragment
def navigation_fragment():
    """Navigation section that won't trigger full page reruns"""
    st.sidebar.header("📋 Navigation")

    # Your page navigation logic here
    if st.sidebar.button("📁 Upload Data"):
        st.switch_page("pages/1_Upload_data.py")

    if st.sidebar.button("📊 Data Overview"):
        st.switch_page("pages/2_Data_overview.py")

@st.fragment
def validation_statistics_fragment():
    """Display validation statistics in sidebar as vertical rows"""
    session_table = st.session_state.session_table

    if session_table.is_validation_completed():
        validated_data = session_table.get_validated_data()
        if validated_data is not None:
            valid_count = len(validated_data[validated_data["IsValid"] == True])
            invalid_count = len(validated_data[validated_data["IsValid"] == False])
            total_count = len(validated_data)
            accuracy = valid_count / total_count * 100 if total_count > 0 else 0

            st.sidebar.header("📊 Data Quality")

            # Convert 4 columns to 4 rows
            st.sidebar.metric(
                "✅ Valid Rows",
                valid_count,
                f"{valid_count/total_count*100:.1f}%" if total_count > 0 else "0%"
            )

            st.sidebar.metric(
                "❌ Invalid Rows",
                invalid_count,
                f"{invalid_count/total_count*100:.1f}%" if total_count > 0 else "0%"
            )

            st.sidebar.metric("📊 Total Rows", total_count)

            st.sidebar.metric("🎯 Data Quality", f"{accuracy:.1f}%")
