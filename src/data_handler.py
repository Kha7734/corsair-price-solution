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
            st.session_state.session_data = {
                "original_data": None,
                "validated_data": None,
                "validation_completed": False,
                "file_info": None,
                "validation_log": [],
                "selected_countries": [],  # Add country selection to session
                "confirmed_data": None,  # Store confirmed data for selected country
                "confirmation_completed": False,
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
            invalid_count = len(validated_data[validated_data["IsValid"] == False])
            return invalid_count == 0
        return False

    def get_selected_countries(self):
        """Get selected countries list"""
        return st.session_state.session_data.get("selected_countries", [])

    def set_selected_countries(self, countries):
        """Set selected countries list"""
        if set(st.session_state.session_data.get("selected_countries", [])) != set(countries):
            st.session_state.session_data["selected_countries"] = countries
            # Reset confirmation when countries change
            st.session_state.session_data["confirmed_data"] = None
            st.session_state.session_data["confirmation_completed"] = False
            self.log_message(f"Selected countries changed to: {', '.join(countries)}")

    def clear_all(self):
        """Clear all session data"""
        st.session_state.session_data = {
            "original_data": None,
            "validated_data": None,
            "validation_completed": False,
            "file_info": None,
            "validation_log": [],
            "confirmed_data": None,
            "confirmation_completed": False,
            "selected_countries": [],
        }
        self.log_message("Cleared all session data")

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
    """Validate the entire original dataset"""
    original_data = session_table.get_original_data()

    if original_data is None:
        session_table.log_message("Validation failed: No data to validate", "ERROR")
        return None

    session_table.log_message("Starting data validation on entire dataset")

    try:
        # Required columns
        required_columns = [
            "ProductID",
            "ItemID",
            "ActualPrice",
            "PromoPrice",
            "StartDate",
            "EndDate",
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

        session_table.log_message("All required columns found")

        # Create validation copy
        validation_df = original_data.copy()
        validation_df["ValidationErrors"] = ""
        validation_df["IsValid"] = True

        session_table.log_message(f"Validating {len(validation_df)} rows")

        # Validation statistics
        validation_stats = {
            "total_rows": len(validation_df),
            "valid_rows": 0,
            "invalid_rows": 0,
            "error_types": {},
        }

        # Validate each row
        for idx, row in validation_df.iterrows():
            try:
                errors = []

                # Check required fields
                for col in required_columns:
                    if pd.isna(row[col]) or str(row[col]).strip() == "":
                        error = f"Missing {col}"
                        errors.append(error)
                        validation_stats["error_types"][error] = (
                            validation_stats["error_types"].get(error, 0) + 1
                        )

                # Check numeric fields
                try:
                    actual_price = float(row["ActualPrice"])
                    if actual_price <= 0:
                        error = "ActualPrice must be > 0"
                        errors.append(error)
                        validation_stats["error_types"][error] = (
                            validation_stats["error_types"].get(error, 0) + 1
                        )
                except:
                    error = "Invalid ActualPrice"
                    errors.append(error)
                    validation_stats["error_types"][error] = (
                        validation_stats["error_types"].get(error, 0) + 1
                    )

                try:
                    promo_price = float(row["PromoPrice"])
                    if promo_price < 0:
                        error = "PromoPrice must be >= 0"
                        errors.append(error)
                        validation_stats["error_types"][error] = (
                            validation_stats["error_types"].get(error, 0) + 1
                        )
                except:
                    error = "Invalid PromoPrice"
                    errors.append(error)
                    validation_stats["error_types"][error] = (
                        validation_stats["error_types"].get(error, 0) + 1
                    )

                # Date validation
                try:
                    start_date = pd.to_datetime(row["StartDate"])
                    end_date = pd.to_datetime(row["EndDate"])
                    if start_date >= end_date:
                        error = "StartDate must be before EndDate"
                        errors.append(error)
                        validation_stats["error_types"][error] = (
                            validation_stats["error_types"].get(error, 0) + 1
                        )
                except Exception:
                    error = "Invalid date format"
                    errors.append(error)
                    validation_stats["error_types"][error] = (
                        validation_stats["error_types"].get(error, 0) + 1
                    )

                # Update validation results
                if errors:
                    validation_df.at[idx, "ValidationErrors"] = "; ".join(errors)
                    validation_df.at[idx, "IsValid"] = False
                    validation_stats["invalid_rows"] += 1
                else:
                    validation_stats["valid_rows"] += 1

            except Exception as row_error:
                error_msg = f"Error validating row {idx}: {str(row_error)}"
                session_table.log_message(error_msg, "ERROR")
                validation_df.at[idx, "ValidationErrors"] = (
                    f"Validation error: {str(row_error)}"
                )
                validation_df.at[idx, "IsValid"] = False
                validation_stats["invalid_rows"] += 1

        # Store validation results
        session_table.store_validated_data(validation_df)

        # Log validation summary
        session_table.log_message(
            f"Validation completed - Valid: {validation_stats['valid_rows']}, Invalid: {validation_stats['invalid_rows']}"
        )
        session_table.log_message(f"Error breakdown: {validation_stats['error_types']}")

        return validation_df

    except Exception as e:
        error_msg = f"Critical validation error: {str(e)}"
        session_table.log_message(error_msg, "ERROR")
        st.error(f"❌ Validation failed: {str(e)}")
        return None


def prepare_display_data(view_filter, row_limit):
    """Prepare data for display based on filters"""
    try:
        if not session_table.is_validation_completed():
            # Show preview of original data
            original_data = session_table.get_original_data()
            if original_data is not None:
                limit = int(row_limit) if row_limit != "All" else len(original_data)
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
        session_table.log_message(f"Display preparation error: {str(e)}", "ERROR")
        return None

def has_data_for_overview(self):
    """Check if there's enough data to show the overview tab"""
    return self.get_original_data() is not None
