"""Assistant message processing for Streamlit"""
import streamlit as st
import json


def parse_partial_json(json_str):
    """Parse partial JSON safely"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try to fix common issues
        json_str = json_str.strip()
        if not json_str.startswith("{"):
            json_str = "{" + json_str
        if not json_str.endswith("}"):
            json_str = json_str + "}"
        try:
            return json.loads(json_str)
        except:
            return {}


def process_messages_streamlit(response):
    """Process streaming messages from API response"""
    buffer = ""
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            buffer += decoded
            
            # Process complete SSE messages
            lines = buffer.split("\n\n")
            buffer = lines.pop() if lines else ""
            
            for line in lines:
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        return
                    
                    try:
                        data = json.loads(data_str)
                        handle_event(data)
                    except json.JSONDecodeError:
                        continue


def handle_event(data):
    """Handle a single event from the stream"""
    event = data.get("event")
    event_data = data.get("data", {})
    
    if event == "response.output_text.delta":
        handle_output_text_delta(event_data)
    elif event == "response.output_text.annotation.added":
        handle_annotation_added(event_data)
    elif event == "response.output_item.added":
        handle_output_item_added(event_data)
    elif event == "response.output_item.done":
        handle_output_item_done(event_data)
    elif event == "response.function_call_arguments.delta":
        handle_function_call_arguments_delta(event_data)
    elif event == "response.function_call_arguments.done":
        handle_function_call_arguments_done(event_data)
    elif event == "response.mcp_call_arguments.delta":
        handle_mcp_call_arguments_delta(event_data)
    elif event == "response.mcp_call_arguments.done":
        handle_mcp_call_arguments_done(event_data)
    elif event == "response.web_search_call.completed":
        handle_web_search_completed(event_data)
    elif event == "response.file_search_call.completed":
        handle_file_search_completed(event_data)
    elif event == "response.code_interpreter_call_code.delta":
        handle_code_interpreter_code_delta(event_data)
    elif event == "response.code_interpreter_call_code.done":
        handle_code_interpreter_code_done(event_data)
    elif event == "response.code_interpreter_call.completed":
        handle_code_interpreter_completed(event_data)
    elif event == "response.completed":
        handle_response_completed(event_data)


def handle_output_text_delta(data):
    """Handle output text delta"""
    delta = data.get("delta", "")
    item_id = data.get("item_id")
    
    if isinstance(delta, str):
        # Find or create assistant message
        last_msg = None
        for msg in reversed(st.session_state.chat_messages):
            if msg.get("type") == "message" and msg.get("role") == "assistant":
                if not msg.get("id") or msg.get("id") == item_id:
                    last_msg = msg
                    break
        
        if last_msg:
            if "content" in last_msg and len(last_msg["content"]) > 0:
                last_msg["content"][0]["text"] = last_msg["content"][0].get("text", "") + delta
        else:
            # Create new assistant message
            st.session_state.chat_messages.append({
                "type": "message",
                "role": "assistant",
                "id": item_id,
                "content": [{"type": "output_text", "text": delta}],
            })


def handle_annotation_added(data):
    """Handle annotation added"""
    annotation = data.get("annotation", {})
    item_id = data.get("item_id")
    
    # Find the message and add annotation
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "message":
            if "content" in msg and len(msg["content"]) > 0:
                if "annotations" not in msg["content"][0]:
                    msg["content"][0]["annotations"] = []
                msg["content"][0]["annotations"].append(normalize_annotation(annotation))


def handle_output_item_added(data):
    """Handle output item added"""
    item = data.get("item", {})
    if not item or not item.get("type"):
        return
    
    item_type = item.get("type")
    
    if item_type == "message":
        text = item.get("content", {}).get("text", "")
        annotations = item.get("content", {}).get("annotations", [])
        st.session_state.chat_messages.append({
            "type": "message",
            "role": "assistant",
            "content": [{
                "type": "output_text",
                "text": text,
                "annotations": [normalize_annotation(a) for a in annotations],
            }],
        })
        st.session_state.conversation_items.append({
            "role": "assistant",
            "content": [{"type": "output_text", "text": text}],
        })
    
    elif item_type == "function_call":
        st.session_state.chat_messages.append({
            "type": "tool_call",
            "tool_type": "function_call",
            "status": "in_progress",
            "id": item.get("id"),
            "name": item.get("name"),
            "arguments": item.get("arguments", ""),
            "parsedArguments": {},
            "output": None,
        })
    
    elif item_type == "web_search_call":
        st.session_state.chat_messages.append({
            "type": "tool_call",
            "tool_type": "web_search_call",
            "status": item.get("status", "in_progress"),
            "id": item.get("id"),
        })
    
    elif item_type == "file_search_call":
        st.session_state.chat_messages.append({
            "type": "tool_call",
            "tool_type": "file_search_call",
            "status": item.get("status", "in_progress"),
            "id": item.get("id"),
        })
    
    elif item_type == "mcp_call":
        st.session_state.chat_messages.append({
            "type": "tool_call",
            "tool_type": "mcp_call",
            "status": "in_progress",
            "id": item.get("id"),
            "name": item.get("name"),
            "arguments": item.get("arguments", ""),
            "parsedArguments": parse_partial_json(item.get("arguments", "")) if item.get("arguments") else {},
            "output": None,
        })
    
    elif item_type == "code_interpreter_call":
        st.session_state.chat_messages.append({
            "type": "tool_call",
            "tool_type": "code_interpreter_call",
            "status": item.get("status", "in_progress"),
            "id": item.get("id"),
            "code": "",
            "files": [],
        })


def handle_output_item_done(data):
    """Handle output item done"""
    item = data.get("item", {})
    item_id = item.get("id")
    
    # Update tool call with call_id
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["call_id"] = item.get("call_id")
            
            # Handle function call output
            if msg.get("tool_type") == "function_call":
                # Execute function (this would need to call the function handler)
                # For now, we'll just mark it as completed
                msg["status"] = "completed"
                msg["output"] = item.get("output")
            
            elif msg.get("tool_type") == "mcp_call":
                msg["status"] = "completed"
                msg["output"] = item.get("output")
    
    st.session_state.conversation_items.append(item)


def handle_function_call_arguments_delta(data):
    """Handle function call arguments delta"""
    delta = data.get("delta", "")
    item_id = data.get("item_id")
    
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["arguments"] = msg.get("arguments", "") + delta
            try:
                msg["parsedArguments"] = parse_partial_json(msg["arguments"])
            except:
                pass


def handle_function_call_arguments_done(data):
    """Handle function call arguments done"""
    item_id = data.get("item_id")
    final_args = data.get("arguments", "")
    
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["arguments"] = final_args
            msg["parsedArguments"] = parse_partial_json(final_args)
            msg["status"] = "completed"


def handle_mcp_call_arguments_delta(data):
    """Handle MCP call arguments delta"""
    delta = data.get("delta", "")
    item_id = data.get("item_id")
    
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["arguments"] = msg.get("arguments", "") + delta
            try:
                msg["parsedArguments"] = parse_partial_json(msg["arguments"])
            except:
                pass


def handle_mcp_call_arguments_done(data):
    """Handle MCP call arguments done"""
    item_id = data.get("item_id")
    final_args = data.get("arguments", "")
    
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["arguments"] = final_args
            msg["parsedArguments"] = parse_partial_json(final_args)
            msg["status"] = "completed"


def handle_web_search_completed(data):
    """Handle web search completed"""
    item_id = data.get("item_id")
    output = data.get("output")
    
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["status"] = "completed"
            msg["output"] = output


def handle_file_search_completed(data):
    """Handle file search completed"""
    item_id = data.get("item_id")
    output = data.get("output")
    
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["status"] = "completed"
            msg["output"] = output


def handle_code_interpreter_code_delta(data):
    """Handle code interpreter code delta"""
    delta = data.get("delta", "")
    item_id = data.get("item_id")
    
    for msg in reversed(st.session_state.chat_messages):
        if (msg.get("type") == "tool_call" and
            msg.get("tool_type") == "code_interpreter_call" and
            msg.get("id") == item_id and
            msg.get("status") != "completed"):
            msg["code"] = msg.get("code", "") + delta
            break


def handle_code_interpreter_code_done(data):
    """Handle code interpreter code done"""
    code = data.get("code", "")
    item_id = data.get("item_id")
    
    for msg in reversed(st.session_state.chat_messages):
        if (msg.get("type") == "tool_call" and
            msg.get("tool_type") == "code_interpreter_call" and
            msg.get("id") == item_id):
            msg["code"] = code
            msg["status"] = "completed"
            break


def handle_code_interpreter_completed(data):
    """Handle code interpreter completed"""
    item_id = data.get("item_id")
    
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["status"] = "completed"


def handle_response_completed(data):
    """Handle response completed"""
    response = data.get("response", {})
    output = response.get("output", [])
    
    # Handle MCP tools list
    for item in output:
        if item.get("type") == "mcp_list_tools":
            st.session_state.chat_messages.append({
                "type": "mcp_list_tools",
                "id": item.get("id"),
                "server_label": item.get("server_label"),
                "tools": item.get("tools", []),
            })
        
        elif item.get("type") == "mcp_approval_request":
            st.session_state.chat_messages.append({
                "type": "mcp_approval_request",
                "id": item.get("id"),
                "server_label": item.get("server_label"),
                "name": item.get("name"),
                "arguments": item.get("arguments"),
            })


def normalize_annotation(annotation):
    """Normalize annotation format"""
    return {
        **annotation,
        "fileId": annotation.get("file_id") or annotation.get("fileId"),
        "containerId": annotation.get("container_id") or annotation.get("containerId"),
    }

