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

def detect_datetime_format(series):
    """Detect the datetime format from a pandas Series and return format string"""
    if series.empty:
        return "Unknown"
    
    # Filter out NaN values and get a sample
    non_nan_values = series.dropna()
    if len(non_nan_values) == 0:
        return "Unknown"
    
    # Take a sample of values for format detection
    sample_size = min(10, len(non_nan_values))
    sample_values = non_nan_values.head(sample_size)
    
    # Common format patterns to detect
    format_patterns = {
        r'^\d{4}-\d{2}-\d{2}$': 'yyyy-mm-dd',
        r'^\d{2}/\d{2}/\d{4}$': 'mm/dd/yyyy',
        r'^\d{1,2}/\d{1,2}/\d{4}$': 'm/d/yyyy',
        r'^\d{2}-\d{2}-\d{4}$': 'mm-dd-yyyy',
        r'^\d{2}\.\d{2}\.\d{4}$': 'mm.dd.yyyy',
        r'^\d{4}/\d{2}/\d{2}$': 'yyyy/mm/dd',
        r'^\d{8}$': 'yyyymmdd',
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$': 'yyyy-mm-dd hh:mm:ss',
        r'^[A-Za-z]{3} \d{1,2}, \d{4}$': 'Mon d, yyyy',
    }
    
    import re
    string_values = sample_values.astype(str)
    
    # Count matches for each pattern
    pattern_counts = {}
    for pattern, format_name in format_patterns.items():
        matches = sum(1 for val in string_values if re.match(pattern, val.strip()))
        if matches > 0:
            pattern_counts[format_name] = matches
    
    # Return the most common format
    if pattern_counts:
        most_common_format = max(pattern_counts.items(), key=lambda x: x[1])[0]
        return most_common_format
    
    return 'datetime'  # Generic fallback

def column_headers_for_dates(df):
    """Enhance column headers by adding format information for date columns"""
    enhanced_df = df.copy()
    new_columns = []
    
    date_column_names = ['Start Date', 'End Date', 'StartDate', 'EndDate']
    
    for col in df.columns:
        if col in date_column_names:
            try:
                if len(df[col].dropna()) > 0:
                    detected_format = detect_datetime_format(df[col])
                    if detected_format != 'Unknown':
                        new_col_name = f"{col} ({detected_format})"
                        new_columns.append(new_col_name)
                    else:
                        new_columns.append(col)
                else:
                    new_columns.append(col)
            except Exception:
                new_columns.append(col)
        else:
            new_columns.append(col)
    
    enhanced_df.columns = new_columns
    return enhanced_df

def _display_data_table(session_table):
    """Display the data table with enhanced datetime format headers"""
    try:
        view_filter = st.session_state.get("view_filter", "All Rows")
        row_limit = st.session_state.get("row_limit", 10)

        display_df = prepare_display_data(view_filter, row_limit)
        if display_df is not None:
            # Enhance column headers for date columns
            enhanced_df = column_headers_for_dates(display_df)
            
            st.dataframe(enhanced_df)

            selected_country = session_table.get_selected_country()
            if session_table.is_validation_completed():
                st.caption(
                    f"Showing {len(enhanced_df)} rows from {view_filter.lower()} for {selected_country}")
            else:
                st.caption(
                    f"Showing preview of first {len(enhanced_df)} rows for {selected_country}")
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
