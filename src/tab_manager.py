"""Tab management for the Price Intelligence Solution"""
import streamlit as st
from src.data_handler import SessionTable

class TabManager:
    """Manages tab state and navigation"""
    
    TABS = {
        "upload": {"name": "📁 Upload Data", "index": 0},
        "overview": {"name": "📊 Data Overview", "index": 1}
    }
    
    def __init__(self, session_table: SessionTable):
        self.session_table = session_table
        
        # Initialize tab state
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = "upload"
    
    def render_left_panel(self):
        """Render the left panel with tab navigation"""
        st.sidebar.title("Navigation")
        
        # Auto-switch logic: move to overview when data is loaded
        should_auto_switch = (
            st.session_state.current_tab == "upload" and 
            self.session_table.get_original_data() is not None
        )
        
        if should_auto_switch:
            st.session_state.current_tab = "overview"
            # Force rerun to update the UI immediately
            st.rerun()
        
        # Render tab buttons
        for tab_key, tab_info in self.TABS.items():
            # Determine if tab should be disabled
            disabled = self._is_tab_disabled(tab_key)
            
            # Style active tab differently
            if st.session_state.current_tab == tab_key:
                button_type = "tertiary"
            else:
                button_type = "secondary"
            
            if st.sidebar.button(
                tab_info["name"], 
                key=f"tab_{tab_key}",
                disabled=disabled,
                type=button_type,
                use_container_width=True
            ):
                if not disabled:
                    st.session_state.current_tab = tab_key
                    st.rerun()
        
        # Add separator
        st.sidebar.markdown("---")
        
        # Add session info
        self._render_session_info()
    
    def _is_tab_disabled(self, tab_key):
        """Determine if a tab should be disabled"""
        if tab_key == "overview":
            # Data Overview tab is disabled if no data is loaded
            return self.session_table.get_original_data() is None
        return False
    
    def _render_session_info(self):
        """Render session information in sidebar"""
        original_data = self.session_table.get_original_data()
        
        if original_data is not None:
            st.sidebar.success("✅ Data Loaded")
            st.sidebar.caption(f"Rows: {len(original_data)}")
            st.sidebar.caption(f"Columns: {len(original_data.columns)}")
            
            if self.session_table.is_validation_completed():
                validated_data = self.session_table.get_validated_data()
                valid_count = len(validated_data[validated_data['IsValid'] == True])
                st.sidebar.caption(f"Valid: {valid_count}")
                
            selected_country = self.session_table.get_selected_country()
            st.sidebar.caption(f"Country: {selected_country}")
        else:
            st.sidebar.info("ℹ️ No data loaded")
    
    def get_current_tab(self):
        """Get the currently selected tab"""
        return st.session_state.current_tab
    
    def switch_to_tab(self, tab_key):
        """Programmatically switch to a specific tab"""
        if tab_key in self.TABS and not self._is_tab_disabled(tab_key):
            st.session_state.current_tab = tab_key
            st.rerun()