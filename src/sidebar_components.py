import streamlit as st


@st.fragment
def navigation_fragment():
    """Navigation section that won't trigger full page reruns"""
    st.sidebar.header("📋 Navigation")

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
            valid_count = len(
                validated_data[validated_data["IsValid"] == True])
            invalid_count = len(
                validated_data[validated_data["IsValid"] == False])
            total_count = len(validated_data)
            accuracy = valid_count / total_count * 100 if total_count > 0 else 0

            st.sidebar.header("📊 Data Quality")

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
