import streamlit as st
import snowflake.connector
import logging
from datetime import datetime
from snowflake.connector.pandas_tools import write_pandas

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_snowflake_connection():
    """Establishes a Snowflake connection."""
    try:
        conn = snowflake.connector.connect(
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["programmatic_access_token"],
            account=st.secrets["snowflake"]["account"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"],
            role=st.secrets["snowflake"]["role"]
        )
        logger.info("Successfully connected to Snowflake.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to Snowflake: {e}")
        st.error(f"Error connecting to Snowflake: {e}")
        return None

def upload_dataframe_to_snowflake(df, table_name, session_table=None):
    """
    Uploads a DataFrame to Snowflake using the efficient write_pandas method.
    """
    conn = None
    try:
        conn = get_snowflake_connection()
        if conn is None:
            if session_table:
                session_table.log_message("Failed to connect to Snowflake", "ERROR")
            return False

        df_to_upload = df.copy()
        df_to_upload.columns = [col.replace(' ', '_').replace('-', '_').upper() for col in df.columns]

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df_to_upload,
            table_name=table_name,
            auto_create_table=True,
            overwrite=False
        )
        
        return success

    except Exception as e:
        logger.error(f"Error during Snowflake upload: {str(e)}")
        # Re-raise the exception so the calling function can handle it
        raise e
    finally:
        if conn:
            conn.close()

def upload_original_data_to_snowflake(session_table, table_name_prefix="original_data"):
    """
    Uploads original data from the SessionTable to Snowflake.
    This is the main function called from the modal.
    """
    result = {
        "success": False,
        "message": "",
        "table_name": "",
        "rows_uploaded": 0,
        "upload_time": None
    }
    
    try:
        original_data = session_table.get_original_data()
        if original_data is None or original_data.empty:
            result["message"] = "No original data available to upload."
            return result
        
        # Get selected country
        selected_country = session_table.get_selected_country() or "unknown"
        
        # Create a copy of original data and add selected_country column
        data_with_country = original_data.copy()
        data_with_country['selected_country'] = selected_country
        
        # Generate table name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        table_name = f"{table_name_prefix}_{selected_country}_{timestamp}".upper()
        
        result["table_name"] = table_name
        result["rows_uploaded"] = len(data_with_country)
        
        session_table.log_message(f"Starting upload to table: {table_name}")
        
        # Upload the data with selected_country column
        success = upload_dataframe_to_snowflake(data_with_country, table_name, session_table)
        
        if success:
            result["success"] = True
            result["upload_time"] = datetime.now()
            result["message"] = f"Successfully uploaded {len(data_with_country)} rows to table: **{table_name}**"
            session_table.log_message(f"Upload completed successfully for table: {table_name}")
        else:
            result["message"] = "Upload to Snowflake failed. Please check the logs for details."
            session_table.log_message("Upload to Snowflake failed", "ERROR")
            
    except Exception as e:
        error_message = f"An unexpected error occurred during the upload process: {str(e)}"
        result["message"] = error_message
        session_table.log_message(error_message, "ERROR")
        logger.error(error_message)
    
    return result