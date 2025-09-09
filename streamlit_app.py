import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io

# Set page config
st.set_page_config(
    page_title="Price Intelligence Solution",
    page_icon="💰",
    layout="wide"
)

def upload_file_section():
    st.header("📁 Upload File")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your promotion data file"
    )
    
    if uploaded_file is not None:
        try:
            # Parse file based on extension
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! Found {len(df)} rows.")
            
            # Store in session state
            st.session_state.data = df
            st.session_state.validated = False
            
            # Show preview
            st.subheader("📋 Data Preview (First 5 rows)")
            st.dataframe(df.head())
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            return None
    
    return None

def validate_data(df):
    """Simple validation function - we'll expand this later"""
    if df is None:
        return None
    
    # Required columns
    required_columns = ['ProductID', 'ItemID', 'ActualPrice', 'PromoPrice', 'StartDate', 'EndDate', 'Country']
    
    # Check if required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
        return None
    
    # Create a copy for validation
    validation_df = df.copy()
    validation_df['ValidationErrors'] = ''
    validation_df['IsValid'] = True
    
    # Basic validation rules
    for idx, row in validation_df.iterrows():
        errors = []
        
        # Check required fields
        for col in required_columns:
            if pd.isna(row[col]) or str(row[col]).strip() == '':
                errors.append(f"Missing {col}")
        
        # Check numeric fields
        try:
            actual_price = float(row['ActualPrice'])
            if actual_price <= 0:
                errors.append("ActualPrice must be > 0")
        except:
            errors.append("Invalid ActualPrice")
        
        try:
            promo_price = float(row['PromoPrice'])
            if promo_price < 0:
                errors.append("PromoPrice must be >= 0")
        except:
            errors.append("Invalid PromoPrice")
        
        # Update validation results
        if errors:
            validation_df.at[idx, 'ValidationErrors'] = '; '.join(errors)
            validation_df.at[idx, 'IsValid'] = False
    
    return validation_df


def verification_section():
    if st.session_state.data is not None:
        st.header("🔍 Verification")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🔍 Verify Data", type="primary"):
                with st.spinner("Validating data..."):
                    validation_results = validate_data(st.session_state.data)
                    st.session_state.validation_results = validation_results
                    st.session_state.validated = True
        
        with col2:
            if st.button("🗑️ Clear Data"):
                st.session_state.data = None
                st.session_state.validated = False
                st.session_state.validation_results = None
                st.rerun()

def results_section():
    if st.session_state.validated and st.session_state.validation_results is not None:
        st.header("📊 Validation Results")
        
        df = st.session_state.validation_results
        valid_count = len(df[df['IsValid'] == True])
        invalid_count = len(df[df['IsValid'] == False])
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Valid Rows", valid_count)
        with col2:
            st.metric("❌ Invalid Rows", invalid_count)
        with col3:
            st.metric("📈 Total Rows", len(df))
        
        # Display options
        view_option = st.radio(
            "View:",
            ["Valid Rows", "Invalid Rows", "All Rows"],
            horizontal=True
        )
        
        # Filter data based on selection
        if view_option == "Valid Rows":
            display_df = df[df['IsValid'] == True].drop(['IsValid'], axis=1)
        elif view_option == "Invalid Rows":
            display_df = df[df['IsValid'] == False].drop(['IsValid'], axis=1)
        else:
            display_df = df.drop(['IsValid'], axis=1)
        
        st.dataframe(display_df, width='stretch')

def main():
    st.title("💰 Price Intelligence Solution")
    st.markdown("Upload promotion data (CSV/Excel) to validate and process")
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'validated' not in st.session_state:
        st.session_state.validated = False
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    
    # Upload section
    upload_file_section()
    
    # Verification section
    verification_section()
    
    # Results section
    results_section()


if __name__ == "__main__":
    main()