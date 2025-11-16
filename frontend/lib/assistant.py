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
    """Process streaming messages from API response (non-realtime version)"""
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


def process_messages_streamlit_realtime(response):
    """Process streaming messages from API response"""
    import streamlit as st
    
    # Process all events first, then rerun once at the end
    # Streamlit doesn't support true real-time updates during blocking operations
    buffer = ""
    event_count = 0
    
    print("Starting to process stream...")
    
    try:
        # Read the stream content
        raw_content = b""
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                raw_content += chunk
        
        # Decode the content
        content = raw_content.decode("utf-8")
        print(f"Received {len(content)} characters of stream data")
        print(f"First 500 chars: {content[:500]}")
        
        # Split by double newlines (SSE format)
        messages = content.split("\n\n")
        print(f"Found {len(messages)} potential SSE messages")
        
        for msg in messages:
            if not msg.strip():
                continue
                
            # Look for data lines
            for line in msg.split("\n"):
                line = line.strip()
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    
                    if data_str == "[DONE]":
                        print(f"Stream complete. Processed {event_count} events.")
                        print(f"Final chat_messages count: {len(st.session_state.chat_messages)}")
                        return
                    
                    if not data_str:
                        continue
                    
                    try:
                        data = json.loads(data_str)
                        event_count += 1
                        event_type = data.get('event', 'unknown')
                        print(f"Parsed event #{event_count}: {event_type}")
                        try:
                            handle_event(data)
                        except Exception as e:
                            print(f"Error handling event {event_type}: {e}")
                            import traceback
                            traceback.print_exc()
                            # Continue processing other events
                            continue
                    except json.JSONDecodeError as e:
                        # Log the error for debugging
                        print(f"JSON decode error: {e}")
                        print(f"  Data: {data_str[:200]}")
                        continue
        
        print(f"Stream ended. Processed {event_count} events.")
        print(f"Final chat_messages count: {len(st.session_state.chat_messages)}")
        
        # Check if we need to continue after function call
        if hasattr(st.session_state, 'needs_continuation') and st.session_state.needs_continuation:
            st.session_state.needs_continuation = False
            # Trigger another API call
            from components.chat import process_messages
            print("Function call completed, making another API request with tool output...")
            process_messages()
        
        # If no events were processed, try alternative parsing
        if event_count == 0:
            print("No events found with standard SSE parsing. Trying alternative...")
            # Try parsing the entire content as JSON
            try:
                data = json.loads(content)
                print(f"Parsed as single JSON: {type(data)}")
            except:
                pass
        
    except Exception as e:
        print(f"Error processing stream: {e}")
        import traceback
        traceback.print_exc()


def handle_event(data):
    """Handle a single event from the stream"""
    event = data.get("event")
    event_data = data.get("data", {})
    
    # Debug: print event type to help diagnose issues
    if event:
        print(f"Processing event: {event}")
        if event_data:
            print(f"  Event data keys: {list(event_data.keys())[:5]}")
    
    # Handle different event types
    if event == "response.output_text.delta":
        handle_output_text_delta(event_data)
    elif event == "response.output_text.annotation.added":
        handle_annotation_added(event_data)
    elif event == "response.output_item.added":
        # This might also contain text content
        try:
            handle_output_item_added(event_data)
        except Exception as e:
            print(f"Error handling output_item.added: {e}")
            print(f"  Event data: {event_data}")
            import traceback
            traceback.print_exc()
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
    import streamlit as st
    
    delta = data.get("delta", "")
    item_id = data.get("item_id")
    
    print(f"handle_output_text_delta: delta='{delta[:50] if delta else ''}', item_id={item_id}")
    
    if isinstance(delta, str) and delta:
        # Find or create assistant message
        last_msg = None
        for msg in reversed(st.session_state.chat_messages):
            if msg.get("type") == "message" and msg.get("role") == "assistant":
                # Match by item_id if provided, otherwise use the last assistant message
                if not item_id or msg.get("id") == item_id or not msg.get("id"):
                    last_msg = msg
                    break
        
        if last_msg:
            if "content" in last_msg and len(last_msg["content"]) > 0:
                current_text = last_msg["content"][0].get("text", "")
                last_msg["content"][0]["text"] = current_text + delta
                print(f"  Updated existing message, new length: {len(current_text + delta)}")
            else:
                last_msg["content"] = [{"type": "output_text", "text": delta}]
                print(f"  Added content to existing message")
        else:
            # Create new assistant message
            new_msg = {
                "type": "message",
                "role": "assistant",
                "id": item_id,
                "content": [{"type": "output_text", "text": delta}],
            }
            st.session_state.chat_messages.append(new_msg)
            print(f"  Created new assistant message, total messages: {len(st.session_state.chat_messages)}")


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
    if not item:
        return
    
    # Handle case where item might be a list or dict
    if isinstance(item, list):
        # If item is a list, process the first element or return
        if len(item) == 0:
            return
        item = item[0]
    
    if not isinstance(item, dict) or not item.get("type"):
        return
    
    item_type = item.get("type")
    
    if item_type == "message":
        # Handle content - it might be a dict or a list
        content = item.get("content", {})
        if isinstance(content, list):
            # If content is a list, get the first element
            if len(content) > 0 and isinstance(content[0], dict):
                text = content[0].get("text", "")
                annotations = content[0].get("annotations", [])
            else:
                text = ""
                annotations = []
        elif isinstance(content, dict):
            text = content.get("text", "")
            annotations = content.get("annotations", [])
        else:
            text = str(content) if content else ""
            annotations = []
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
    import streamlit as st
    import requests
    from utils.config import get_api_base_url
    
    item = data.get("item", {})
    item_id = item.get("id")
    
    # Update tool call with call_id
    for msg in st.session_state.chat_messages:
        if msg.get("id") == item_id and msg.get("type") == "tool_call":
            msg["call_id"] = item.get("call_id")
            
            # Handle function call output
            if msg.get("tool_type") == "function_call":
                # Execute function and get output
                function_name = msg.get("name")
                parsed_args = msg.get("parsedArguments", {})
                
                # Call the backend function endpoint
                try:
                    API_BASE_URL = get_api_base_url()
                    if function_name == "get_weather":
                        location = parsed_args.get("location", "")
                        unit = parsed_args.get("unit", "celsius")
                        response = requests.get(
                            f"{API_BASE_URL}/api/functions/get_weather",
                            params={"location": location, "unit": unit},
                            timeout=10
                        )
                        if response.ok:
                            tool_result = response.json()
                        else:
                            tool_result = {"error": f"Function call failed: {response.status_code}"}
                    elif function_name == "get_joke":
                        response = requests.get(
                            f"{API_BASE_URL}/api/functions/get_joke",
                            timeout=10
                        )
                        if response.ok:
                            tool_result = response.json()
                        else:
                            tool_result = {"error": f"Function call failed: {response.status_code}"}
                    else:
                        tool_result = {"error": f"Unknown function: {function_name}"}
                    
                    # Add tool output to conversation
                    import json
                    tool_output_item = {
                        "type": "function_call_output",
                        "call_id": item.get("call_id"),
                        "status": "completed",
                        "output": json.dumps(tool_result),
                    }
                    st.session_state.conversation_items.append(tool_output_item)
                    
                    # Update message with output
                    msg["status"] = "completed"
                    msg["output"] = json.dumps(tool_result)
                    
                    # Trigger another API call with the tool output
                    # This will be handled by checking if we need to continue
                    st.session_state.needs_continuation = True
                    
                except Exception as e:
                    print(f"Error executing function {function_name}: {e}")
                    import json
                    tool_output_item = {
                        "type": "function_call_output",
                        "call_id": item.get("call_id"),
                        "status": "completed",
                        "output": json.dumps({"error": str(e)}),
                    }
                    st.session_state.conversation_items.append(tool_output_item)
                    msg["status"] = "completed"
                    msg["output"] = json.dumps({"error": str(e)})
                    st.session_state.needs_continuation = True
            
            elif msg.get("tool_type") == "mcp_call":
                msg["status"] = "completed"
                msg["output"] = item.get("output")
                # MCP calls already have output from the API
    
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

