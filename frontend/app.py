import streamlit as st
import os

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="OpenAI Responses Starter App",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None  # Hide the menu for full screen experience
)

# Hide Streamlit branding and menu for cleaner full-screen experience
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    
    /* Maximize width usage */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Full width for main content */
    .main {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Ensure sidebar doesn't constrain main content */
    section[data-testid="stSidebar"] {
        min-width: 300px;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Import after st.set_page_config to ensure Streamlit is initialized
from components import chat, tools_panel
from utils.state import init_session_state

# Initialize session state (after Streamlit is initialized)
init_session_state()

# Main layout - use full width with sidebar
chat.render()

# Tools panel in sidebar
with st.sidebar:
    tools_panel.render()

