import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Session table for temporal data storage
class SessionTable:
    """Simple session table to store and manage temporal data"""

    def __init__(self):
        if "session_data" not in st.session_state:
            st.session_state.session_data = self._get_default_state()

    def _get_default_state(self):
        """Returns the default dictionary structure for the session state."""
        return {
            "original_data": None,
            "validated_data": None,
            "validation_completed": False,
            "file_info": None,
            "validation_log": [],
            "selected_country": "",
            "confirmed_data": None,  # Note: This is no longer used but kept for structural consistency
            "confirmation_completed": False, # Note: This is no longer used
            "data_push_completed": False, # This was the missing key
        }

    def store_original_data(self, df, file_info):
        """Store original uploaded data"""
        st.session_state.session_data["original_data"] = df.copy()
        st.session_state.session_data["file_info"] = file_info
        # Reset validation when new data is uploaded
        st.session_state.session_data["validated_data"] = None
        st.session_state.session_data["validation_completed"] = False
        st.session_state.session_data["confirmed_data"] = None
        st.session_state.session_data["confirmation_completed"] = False
        self.log_message(
            f"Stored original data: {len(df)} rows, {len(df.columns)} columns"
        )

    def store_validated_data(self, df):
        """Store validation results"""
        st.session_state.session_data["validated_data"] = df.copy()
        st.session_state.session_data["validation_completed"] = True
        # Reset confirmation when validation changes
        st.session_state.session_data["confirmed_data"] = None
        st.session_state.session_data["confirmation_completed"] = False
        self.log_message("Stored validation results")

    def store_confirmed_data(self, df, country):
        """Store confirmed data for selected country"""
        st.session_state.session_data["confirmed_data"] = df.copy()
        st.session_state.session_data["confirmation_completed"] = True
        self.log_message(f"Confirmed data for country: {country}")

    def get_original_data(self):
        """Get original data"""
        return st.session_state.session_data["original_data"]

    def get_validated_data(self):
        """Get validated data"""
        return st.session_state.session_data["validated_data"]

    def get_confirmed_data(self):
        """Get confirmed data"""
        return st.session_state.session_data["confirmed_data"]

    def is_validation_completed(self):
        """Check if validation is completed"""
        return st.session_state.session_data["validation_completed"]

    def is_confirmation_completed(self):
        """Check if confirmation is completed"""
        return st.session_state.session_data["confirmation_completed"]

    def all_data_is_valid(self):
        """Check if ALL data is valid (no invalid rows)"""
        validated_data = self.get_validated_data()
        if validated_data is not None:
            invalid_count = len(
                validated_data[validated_data["IsValid"] == False])
            return invalid_count == 0
        return False

    def get_selected_country(self):
        """Get selected country list"""
        return st.session_state.session_data.get("selected_country", "")

    def set_selected_country(self, country):
        """Store selected country"""
        current_country = st.session_state.session_data.get("selected_country", None)
        
        # Convert None to empty set for comparison
        current_set = set() if current_country is None else set([current_country]) if isinstance(current_country, str) else set(current_country)
        new_set = set() if country is None else set([country]) if isinstance(country, str) else set(country)
        
        if current_set != new_set:
            st.session_state.session_data["selected_country"] = country
            
            if country is None:
                self.log_message("Country selection cleared")
            else:
                self.log_message(f"Country set to: {country}")

    def set_data_push_completed(self):
        """Mark data push as completed"""
        st.session_state.session_data["data_push_completed"] = True
        self.log_message("Data push marked as completed")

    def is_data_push_completed(self):
        """Check if data push is completed"""
        return st.session_state.session_data.get("data_push_completed", False)

    def clear_push_status(self):
        """Clear data push status"""
        st.session_state.session_data["data_push_completed"] = False
        self.log_message("Data push status cleared")


    def clear_all(self):
        """Clears all data from the session, resetting it to the initial state."""
        st.session_state.session_data = self._get_default_state()
        self._clear_modal_states()
        self.log_message("Cleared all session data")

    def _clear_modal_states(self):
        """Clear all modal-related session states."""
        modal_keys = [
            'show_confirmation_modal',
            'show_processing_modal', 
            'show_success_modal',
            'show_error_modal',
            'data_push_completed',
            'modal_data'
        ]
        for key in modal_keys:
            if key in st.session_state:
                if key == 'modal_data':
                    st.session_state[key] = {}
                else:
                    st.session_state[key] = False

    def log_message(self, message, level="INFO"):
        """Add message to validation log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        st.session_state.session_data["validation_log"].append(log_entry)

        # Also log to system
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

    def get_logs(self, limit=50):
        """Get recent log messages"""
        logs = st.session_state.session_data["validation_log"]
        return logs[-limit:] if len(logs) > limit else logs


# # Initialize session table
session_table = SessionTable()


def validate_data():
    """Validate the entire original dataset with vectorized validation"""
    original_data = session_table.get_original_data()
    if original_data is None:
        session_table.log_message(
            "Validation failed: No data to validate", "ERROR")
        return None

    session_table.log_message("Starting data validation on entire dataset")

    try:
        # Required columns for validation
        required_columns = [
            "Category",
            "Item",
            "Density",
            "MSRP",
            "PROMO",
            "Discount",
            "Start Date",
            "End Date"
        ]

        # Check if required columns exist
        missing_columns = [
            col for col in required_columns if col not in original_data.columns
        ]

        if missing_columns:
            error_msg = f"Missing required columns: {', '.join(missing_columns)}"
            session_table.log_message(error_msg, "ERROR")
            st.error(f"❌ {error_msg}")
            return None

        # Create validation copy
        validation_df = original_data.copy()
        validation_df["ValidationErrors"] = ""
        validation_df["IsValid"] = True

        # Vectorized validation functions
        def validate_text_fields(df, columns):
            """Validate text fields are not empty"""
            errors = []
            for col in columns:
                mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
                errors.append((mask, f"Missing {col}"))
            return errors

        def validate_numeric(df, column, condition, error_msg):
            """Validate numeric columns based on a condition"""
            try:
                # Convert to numeric, coerce errors to NaN
                numeric_col = pd.to_numeric(df[column], errors='coerce')
                # Create mask based on condition
                mask = (~numeric_col.notnull()) | (~condition(numeric_col))
                return [(mask, error_msg)]
            except Exception:
                # If conversion fails completely
                return [(pd.Series([True]*len(df), index=df.index), f"Invalid {column}")]

        # Collect all validation errors
        all_errors = []

        # Text field validation
        text_fields = ["Category", "Item", "Density"]
        all_errors.extend(validate_text_fields(validation_df, text_fields))

        # Numeric validations with vectorized checks
        all_errors.extend(validate_numeric(
            validation_df,
            "MSRP",
            lambda x: x > 0,
            "MSRP must be > 0"
        ))

        all_errors.extend(validate_numeric(
            validation_df,
            "PROMO",
            lambda x: x >= 0,
            "PROMO must be >= 0"
        ))

        all_errors.extend(validate_numeric(
            validation_df,
            "Discount",
            lambda x: x <= 0,
            "Discount should be <= 0"
        ))

        # Date validation
        def validate_dates(df):
            """Validate and compare dates"""
            date_errors = []

            # Parse dates
            df['ParsedStartDate'] = pd.to_datetime(df['Start Date'], errors='coerce')
            df['ParsedEndDate'] = pd.to_datetime(df['End Date'], errors='coerce')

            # Invalid date parsing
            date_errors.append((
                df['ParsedStartDate'].isna(),
                "Invalid Start Date"
            ))
            date_errors.append((
                df['ParsedEndDate'].isna(),
                "Invalid End Date"
            ))

            # Date comparison
            date_errors.append((
                df['ParsedStartDate'] >= df['ParsedEndDate'],
                "Start Date must be before End Date"
            ))

            return date_errors

        # Add date validation errors
        all_errors.extend(validate_dates(validation_df))

        # Apply validation errors
        for error_mask, error_msg in all_errors:
            # Accumulate errors for rows
            validation_df.loc[error_mask, 'ValidationErrors'] = validation_df.loc[error_mask, 'ValidationErrors'].fillna('') + error_msg + '; '
            validation_df.loc[error_mask, 'IsValid'] = False

        # Clean up error strings
        validation_df['ValidationErrors'] = validation_df['ValidationErrors'].str.rstrip('; ')

        # Validation statistics
        validation_stats = {
            "total_rows": len(validation_df),
            "valid_rows": sum(validation_df['IsValid']),
            "invalid_rows": sum(~validation_df['IsValid']),
            "error_types": {}
        }

        # Count error types
        error_breakdown = validation_df[~validation_df['IsValid']]['ValidationErrors'].str.split('; ', expand=True).stack()
        validation_stats['error_types'] = error_breakdown.value_counts().to_dict()
        # Store validation results
        session_table.store_validated_data(validation_df)

        # Log validation summary
        session_table.log_message(
            f"Validation completed - Valid: {validation_stats['valid_rows']}, Invalid: {validation_stats['invalid_rows']}"
        )
        session_table.log_message(
            f"Error breakdown: {validation_stats['error_types']}")

        return validation_df

    except Exception as e:
        error_msg = f"Critical validation error: {str(e)}"
        session_table.log_message(error_msg, "ERROR")
        st.error(f"❌ Validation failed: {str(e)}")
        return None


def parse_mm_dd_yyyy(date_value):
    """
    Robustly parse datetime values but only in 'mm-dd-yyyy' format.
    Returns: (parsed_datetime, error_message)
    """
    if pd.isna(date_value) or str(date_value).strip() == '':
        return None, "Empty date value"

    # Define the allowed date formats (month first)
    mm_dd_yyyy_formats = [
        '%m/%d/%Y',  # 12/31/2023
        '%m-%d-%Y',  # 12-31-2023
        '%m.%d.%Y',  # 12.31.2023
        '%m/%d/%y',  # 12/31/23
        '%m-%d-%y',  # 12-31-23
        '%m.%d.%y',   # 12.31.23
        '%m/%d/%Y %H:%M:%S',
        '%m-%d-%Y %H:%M:%S',
    ]

    # Attempt to parse the date using the allowed formats
    for fmt in mm_dd_yyyy_formats:
        try:
            # On non-Windows platforms, we can use %-m and %-d for non-padded month/day
            # but for cross-platform compatibility, we will rely on pandas' flexibility
            parsed_date = pd.to_datetime(date_value, format=fmt, errors='raise')
            if not pd.isna(parsed_date):
                return parsed_date, None
        except (ValueError, TypeError):
            continue
    
    # If all formats fail, return an error
    return None, f"Invalid date format: '{date_value}'. Please use MM/DD/YYYY."



def prepare_display_data(view_filter, row_limit):
    """Prepare data for display based on filters"""
    try:
        if not session_table.is_validation_completed():
            # Show preview of original data
            original_data = session_table.get_original_data()
            if original_data is not None:
                limit = int(row_limit) if row_limit != "All" else len(
                    original_data)
                display_df = original_data.head(limit)

                display_df = display_df.reset_index(drop=True)
                display_df.index = display_df.index + 1
                return display_df
            return None

        # Show validation results
        validated_data = session_table.get_validated_data()
        if validated_data is None:
            return None

        # Add status column
        display_df = validated_data.copy()
        display_df["Status"] = display_df.apply(
            lambda row: "✅" if row["IsValid"] else "❌", axis=1
        )

        # Filter based on validation status
        if view_filter == "Valid Only":
            display_df = display_df[display_df["IsValid"] == True]
        elif view_filter == "Invalid Only":
            display_df = display_df[display_df["IsValid"] == False]

        # Apply row limit
        if row_limit != "All":
            display_df = display_df.head(int(row_limit))

        # Reorder columns
        data_columns = [
            col
            for col in display_df.columns
            if col not in ["IsValid", "ValidationErrors", "Status"]
        ]
        column_order = ["Status"] + data_columns

        # Add ValidationErrors column for invalid rows or all rows view
        if (
            view_filter in ["Invalid Only", "All Rows"]
            and "ValidationErrors" in display_df.columns
        ):
            if not display_df["ValidationErrors"].str.strip().eq("").all():
                column_order.append("ValidationErrors")

        final_df = display_df[column_order]
        final_df = final_df.reset_index(drop=True)
        final_df.index = final_df.index + 1

        return final_df

    except Exception as e:
        session_table.log_message(
            f"Display preparation error: {str(e)}", "ERROR")
        return None


def has_data_for_overview(self):
    """Check if there's enough data to show the overview tab"""
    return self.get_original_data() is not None

