import streamlit as st
import os

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="OpenAI Responses Starter App",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import after st.set_page_config to ensure Streamlit is initialized
from pages import chat, tools_panel
from utils.state import init_session_state

# Initialize session state (after Streamlit is initialized)
init_session_state()

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    chat.render()

with col2:
    with st.sidebar:
        tools_panel.render()

