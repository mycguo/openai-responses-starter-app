"""Tools panel sidebar"""
import streamlit as st
import requests
from utils.state import get_tools_state
from utils.config import get_api_base_url

API_BASE_URL = get_api_base_url()


def render():
    """Render the tools panel"""
    # Title hidden - uncomment to show: st.sidebar.title("⚙️ Tools Configuration")
    
    # File Search
    with st.sidebar.expander("📁 File Search", expanded=False):
        file_search_enabled = st.checkbox(
            "Enable File Search",
            value=st.session_state.file_search_enabled,
            key="file_search_checkbox",
        )
        st.session_state.file_search_enabled = file_search_enabled
        
        if file_search_enabled:
            render_file_search_setup()
    
    # Web Search
    with st.sidebar.expander("🌐 Web Search", expanded=False):
        web_search_enabled = st.checkbox(
            "Enable Web Search",
            value=st.session_state.web_search_enabled,
            key="web_search_checkbox",
        )
        st.session_state.web_search_enabled = web_search_enabled
        
        if web_search_enabled:
            render_web_search_config()
    
    # Code Interpreter
    with st.sidebar.expander("🐍 Code Interpreter", expanded=False):
        code_interpreter_enabled = st.checkbox(
            "Enable Code Interpreter",
            value=st.session_state.code_interpreter_enabled,
            key="code_interpreter_checkbox",
        )
        st.session_state.code_interpreter_enabled = code_interpreter_enabled
    
    # Functions
    with st.sidebar.expander("🔧 Functions", expanded=False):
        functions_enabled = st.checkbox(
            "Enable Functions",
            value=st.session_state.functions_enabled,
            key="functions_checkbox",
        )
        st.session_state.functions_enabled = functions_enabled
        
        if functions_enabled:
            st.info("Available functions: get_weather, get_joke")
    
    # MCP
    with st.sidebar.expander("🔌 MCP", expanded=False):
        mcp_enabled = st.checkbox(
            "Enable MCP",
            value=st.session_state.mcp_enabled,
            key="mcp_checkbox",
        )
        st.session_state.mcp_enabled = mcp_enabled
        
        if mcp_enabled:
            render_mcp_config()
    
    # Google Integration
    with st.sidebar.expander("🔐 Google Integration", expanded=False):
        check_google_status()
        
        google_integration_enabled = st.checkbox(
            "Enable Google Integration",
            value=st.session_state.google_integration_enabled,
            disabled=not st.session_state.google_oauth_configured,
            key="google_integration_checkbox",
        )
        st.session_state.google_integration_enabled = google_integration_enabled
        
        if st.session_state.google_oauth_configured:
            if st.session_state.google_oauth_connected:
                st.success("✅ Google OAuth connected")
            else:
                if st.button("Connect Google Integration"):
                    st.markdown(
                        f'<a href="{API_BASE_URL}/api/google/auth" target="_blank">Click here to connect</a>',
                        unsafe_allow_html=True,
                    )
        else:
            st.warning("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")


def render_file_search_setup():
    """Render file search setup"""
    st.write("**Vector Store**")
    
    if st.session_state.vector_store and st.session_state.vector_store.get("id"):
        st.text(f"ID: {st.session_state.vector_store['id']}")
        st.text(f"Name: {st.session_state.vector_store.get('name', 'N/A')}")
        if st.button("Unlink Vector Store"):
            st.session_state.vector_store = None
            st.rerun()
    else:
        store_id = st.text_input("Vector Store ID", placeholder="vs_XXXX...")
        if st.button("Add Store"):
            if store_id.strip():
                retrieve_vector_store(store_id.strip())
    
    st.markdown("---")
    st.write("**Upload File**")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "md", "py", "js", "ts", "json"])
    
    if uploaded_file is not None:
        store_name = st.text_input("Store Name (for new store)", value="New Store")
        
        if st.button("Upload"):
            upload_file(uploaded_file, store_name)


def retrieve_vector_store(store_id: str):
    """Retrieve vector store by ID"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/vector_stores/retrieve_store",
            params={"vector_store_id": store_id},
        )
        if response.ok:
            store = response.json()
            st.session_state.vector_store = store
            st.success("Vector store retrieved!")
            st.rerun()
        else:
            st.error("Vector store not found")
    except Exception as e:
        st.error(f"Error retrieving vector store: {str(e)}")


def upload_file(uploaded_file, store_name: str):
    """Upload a file to vector store"""
    try:
        import base64
        
        # Read file content
        file_content = uploaded_file.read()
        file_base64 = base64.b64encode(file_content).decode("utf-8")
        
        # Upload file
        response = requests.post(
            f"{API_BASE_URL}/api/vector_stores/upload_file",
            json={
                "fileObject": {
                    "name": uploaded_file.name,
                    "content": file_base64,
                }
            },
        )
        
        if not response.ok:
            st.error("Error uploading file")
            return
        
        file_data = response.json()
        file_id = file_data.get("id")
        
        if not file_id:
            st.error("Error getting file ID")
            return
        
        # Create or use vector store
        vector_store_id = None
        if st.session_state.vector_store and st.session_state.vector_store.get("id"):
            vector_store_id = st.session_state.vector_store["id"]
        else:
            # Create new store
            create_response = requests.post(
                f"{API_BASE_URL}/api/vector_stores/create_store",
                json={"name": store_name},
            )
            if create_response.ok:
                store_data = create_response.json()
                vector_store_id = store_data.get("id")
                st.session_state.vector_store = store_data
        
        if not vector_store_id:
            st.error("Error getting vector store ID")
            return
        
        # Add file to vector store
        add_response = requests.post(
            f"{API_BASE_URL}/api/vector_stores/add_file",
            json={
                "fileId": file_id,
                "vectorStoreId": vector_store_id,
            },
        )
        
        if add_response.ok:
            st.success("File uploaded successfully!")
            retrieve_vector_store(vector_store_id)
            st.rerun()
        else:
            st.error("Error adding file to vector store")
    
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")


def render_web_search_config():
    """Render web search configuration"""
    st.write("**User Location**")
    
    country = st.text_input(
        "Country",
        value=st.session_state.web_search_config.get("user_location", {}).get("country", ""),
        key="web_search_country",
    )
    
    region = st.text_input(
        "Region",
        value=st.session_state.web_search_config.get("user_location", {}).get("region", ""),
        key="web_search_region",
    )
    
    city = st.text_input(
        "City",
        value=st.session_state.web_search_config.get("user_location", {}).get("city", ""),
        key="web_search_city",
    )
    
    st.session_state.web_search_config = {
        "user_location": {
            "type": "approximate",
            "country": country,
            "region": region,
            "city": city,
        }
    }
    
    if st.button("Clear Location"):
        st.session_state.web_search_config = {
            "user_location": {
                "type": "approximate",
                "country": "",
                "region": "",
                "city": "",
            }
        }
        st.rerun()


def render_mcp_config():
    """Render MCP configuration"""
    st.write("**Server Details**")
    
    server_label = st.text_input(
        "Server Label",
        value=st.session_state.mcp_config.get("server_label", ""),
        placeholder="deepwiki",
        key="mcp_server_label",
    )
    
    server_url = st.text_input(
        "Server URL",
        value=st.session_state.mcp_config.get("server_url", ""),
        placeholder="https://example.com/mcp",
        key="mcp_server_url",
    )
    
    allowed_tools = st.text_input(
        "Allowed Tools (comma-separated)",
        value=st.session_state.mcp_config.get("allowed_tools", ""),
        placeholder="tool1,tool2",
        key="mcp_allowed_tools",
    )
    
    skip_approval = st.checkbox(
        "Skip Approval",
        value=st.session_state.mcp_config.get("skip_approval", True),
        key="mcp_skip_approval",
    )
    
    st.session_state.mcp_config = {
        "server_label": server_label,
        "server_url": server_url,
        "allowed_tools": allowed_tools,
        "skip_approval": skip_approval,
    }
    
    if st.button("Clear MCP Config"):
        st.session_state.mcp_config = {
            "server_label": "",
            "server_url": "",
            "allowed_tools": "",
            "skip_approval": True,
        }
        st.rerun()


def check_google_status():
    """Check Google OAuth status"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/google/status")
        if response.ok:
            data = response.json()
            st.session_state.google_oauth_connected = data.get("connected", False)
            st.session_state.google_oauth_configured = data.get("oauthConfigured", False)
    except Exception:
        st.session_state.google_oauth_connected = False
        st.session_state.google_oauth_configured = False

