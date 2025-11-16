"""Session state management for Streamlit app"""
import streamlit as st
from config.constants import INITIAL_MESSAGE, default_vector_store


def init_session_state():
    """Initialize all session state variables"""
    # Conversation state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": INITIAL_MESSAGE.strip()}],
            }
        ]
    
    if "conversation_items" not in st.session_state:
        st.session_state.conversation_items = []
    
    if "is_assistant_loading" not in st.session_state:
        st.session_state.is_assistant_loading = False
    
    # Tools state
    if "web_search_enabled" not in st.session_state:
        st.session_state.web_search_enabled = True  # Enabled by default
    
    if "file_search_enabled" not in st.session_state:
        st.session_state.file_search_enabled = False
    
    if "functions_enabled" not in st.session_state:
        st.session_state.functions_enabled = True  # Enabled by default
    
    if "code_interpreter_enabled" not in st.session_state:
        st.session_state.code_interpreter_enabled = True  # Enabled by default

    if "shell_enabled" not in st.session_state:
        st.session_state.shell_enabled = True  # Enabled by default

    if "apply_patch_enabled" not in st.session_state:
        st.session_state.apply_patch_enabled = True  # Enabled by default

    if "google_integration_enabled" not in st.session_state:
        st.session_state.google_integration_enabled = False
    
    if "mcp_enabled" not in st.session_state:
        st.session_state.mcp_enabled = False
    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = default_vector_store if default_vector_store.get("id") else None
    
    if "web_search_config" not in st.session_state:
        st.session_state.web_search_config = {
            "user_location": {
                "type": "approximate",
                "country": "",
                "city": "",
                "region": "",
            }
        }
    
    if "needs_continuation" not in st.session_state:
        st.session_state.needs_continuation = False
    
    if "mcp_config" not in st.session_state:
        st.session_state.mcp_config = {
            "server_label": "",
            "server_url": "",
            "allowed_tools": "",
            "skip_approval": True,
        }
    
    if "google_oauth_connected" not in st.session_state:
        st.session_state.google_oauth_connected = False
    
    if "google_oauth_configured" not in st.session_state:
        st.session_state.google_oauth_configured = False


def get_tools_state():
    """Get current tools state as dict"""
    return {
        "webSearchEnabled": st.session_state.web_search_enabled,
        "fileSearchEnabled": st.session_state.file_search_enabled,
        "functionsEnabled": st.session_state.functions_enabled,
        "codeInterpreterEnabled": st.session_state.code_interpreter_enabled,
        "shellEnabled": st.session_state.shell_enabled,
        "applyPatchEnabled": st.session_state.apply_patch_enabled,
        "vectorStore": st.session_state.vector_store or {},
        "webSearchConfig": st.session_state.web_search_config,
        "mcpEnabled": st.session_state.mcp_enabled,
        "mcpConfig": st.session_state.mcp_config,
        "googleIntegrationEnabled": st.session_state.google_integration_enabled,
    }

