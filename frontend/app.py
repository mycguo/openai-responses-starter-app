import streamlit as st
import os

from pages import chat, tools_panel
from utils.state import init_session_state

# Page configuration
st.set_page_config(
    page_title="OpenAI Responses Starter App",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    chat.render()

with col2:
    with st.sidebar:
        tools_panel.render()

