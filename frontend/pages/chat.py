"""Chat interface page"""
import streamlit as st
from utils.state import get_tools_state
from config.constants import INITIAL_MESSAGE
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def reset_conversation():
    """Reset the conversation"""
    st.session_state.chat_messages = [
        {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": INITIAL_MESSAGE.strip()}],
        }
    ]
    st.session_state.conversation_items = []
    st.session_state.is_assistant_loading = False


def render():
    """Render the chat interface"""
    col_title, col_reset = st.columns([10, 1])
    with col_title:
        st.title("💬 Chat")
    with col_reset:
        if st.button("🔄 Reset", help="Reset conversation"):
            reset_conversation()
            st.rerun()
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for idx, item in enumerate(st.session_state.chat_messages):
            render_message_item(item, idx)
        
        # Loading indicator
        if st.session_state.is_assistant_loading:
            with st.chat_message("assistant"):
                with st.spinner("Assistant is thinking..."):
                    st.empty()
    
    # Input area
    st.markdown("---")
    
    # Use form to handle input better
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Message",
            height=100,
            placeholder="Type your message here...",
            label_visibility="collapsed",
        )
        send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
    
    if send_button and user_input.strip():
        handle_send_message(user_input.strip())
        st.rerun()


def handle_send_message(message: str):
    """Handle sending a message"""
    if not message.strip():
        return
    
    # Add user message to conversation
    user_item = {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": message}],
    }
    
    user_message = {
        "role": "user",
        "content": message,
    }
    
    st.session_state.conversation_items.append(user_message)
    st.session_state.chat_messages.append(user_item)
    st.session_state.is_assistant_loading = True
    
    # Process messages
    process_messages()


def process_messages():
    """Process messages and get assistant response"""
    tools_state = get_tools_state()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/turn_response",
            json={
                "messages": st.session_state.conversation_items,
                "toolsState": tools_state,
            },
            stream=True,
            headers={"Content-Type": "application/json"},
        )
        
        if not response.ok:
            st.error(f"Error: {response.status_code}")
            st.session_state.is_assistant_loading = False
            return
        
        # Process streaming response
        from lib.assistant import process_messages_streamlit
        process_messages_streamlit(response)
        st.session_state.is_assistant_loading = False
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
        st.session_state.is_assistant_loading = False


def render_message_item(item, idx):
    """Render a single message item"""
    if item["type"] == "message":
        render_message(item)
    elif item["type"] == "tool_call":
        render_tool_call(item)
    elif item["type"] == "mcp_list_tools":
        render_mcp_tools_list(item)
    elif item["type"] == "mcp_approval_request":
        render_mcp_approval(item, idx)


def render_message(item):
    """Render a message"""
    role = item["role"]
    content = item["content"][0]["text"] if item["content"] else ""
    
    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(content)
            
            # Render annotations if present
            if item["content"] and item["content"][0].get("annotations"):
                render_annotations(item["content"][0]["annotations"])


def render_tool_call(item):
    """Render a tool call"""
    tool_type = item.get("tool_type", "unknown")
    status = item.get("status", "in_progress")
    name = item.get("name", "")
    
    with st.expander(f"🔧 {tool_type.replace('_', ' ').title()} - {name or 'Tool Call'}", expanded=True):
        if status == "in_progress":
            st.info("Processing...")
        elif status == "completed":
            st.success("Completed")
        
        # Show arguments if available
        if item.get("arguments"):
            st.code(item["arguments"], language="json")
        
        # Show output if available
        if item.get("output"):
            st.json(item["output"])
        
        # Show code for code interpreter
        if tool_type == "code_interpreter_call" and item.get("code"):
            st.code(item["code"], language="python")
        
        # Show files
        if item.get("files"):
            for f in item["files"]:
                file_url = f"{API_BASE_URL}/api/container_files/content?file_id={f['file_id']}"
                if f.get("container_id"):
                    file_url += f"&container_id={f['container_id']}"
                if f.get("filename"):
                    file_url += f"&filename={f['filename']}"
                st.download_button(
                    label=f"Download {f.get('filename', f['file_id'])}",
                    data=requests.get(file_url).content,
                    file_name=f.get("filename", "file"),
                    mime=f.get("mime_type", "application/octet-stream"),
                )


def render_mcp_tools_list(item):
    """Render MCP tools list"""
    with st.expander(f"📋 MCP Tools - {item.get('server_label', 'Server')}"):
        tools = item.get("tools", [])
        for tool in tools:
            st.text(f"• {tool.get('name', 'Unknown')}: {tool.get('description', '')}")


def render_mcp_approval(item, idx):
    """Render MCP approval request"""
    st.warning(f"🔐 Approval Request: {item.get('name', 'Unknown tool')}")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Approve", key=f"approve_{idx}"):
            handle_approval_response(True, item["id"])
    
    with col2:
        if st.button("Deny", key=f"deny_{idx}"):
            handle_approval_response(False, item["id"])


def handle_approval_response(approve: bool, approval_id: str):
    """Handle approval response"""
    approval_item = {
        "type": "mcp_approval_response",
        "approve": approve,
        "approval_request_id": approval_id,
    }
    
    st.session_state.conversation_items.append(approval_item)
    process_messages()


def render_annotations(annotations):
    """Render annotations"""
    for annotation in annotations:
        if annotation["type"] == "file_citation":
            st.caption(f"📄 File: {annotation.get('filename', 'Unknown')}")
        elif annotation["type"] == "url_citation":
            st.markdown(f"[🔗 {annotation.get('title', 'Link')}]({annotation.get('url', '#')})")
        elif annotation["type"] == "container_file_citation":
            file_id = annotation.get("fileId", "")
            file_url = f"{API_BASE_URL}/api/container_files/content?file_id={file_id}"
            if annotation.get("containerId"):
                file_url += f"&container_id={annotation['containerId']}"
            if annotation.get("filename"):
                file_url += f"&filename={annotation['filename']}"
            st.download_button(
                label=f"📎 {annotation.get('filename', file_id)}",
                data=requests.get(file_url).content,
                file_name=annotation.get("filename", "file"),
            )

