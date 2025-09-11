import streamlit as st
import pandas as pd
from src.data_handler import SessionTable


def upload_file_section():
    """Handle file upload"""
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
