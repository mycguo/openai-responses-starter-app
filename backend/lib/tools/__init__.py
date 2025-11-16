# Tools package
from typing import Dict, Any, List, Optional
from lib.tools.connectors import get_google_connector_tools

# Import from config
from config.tools_list import tools_list


async def get_tools(tools_state: Dict[str, Any], request: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Get tools configuration based on tools state"""
    web_search_enabled = tools_state.get("webSearchEnabled", False)
    file_search_enabled = tools_state.get("fileSearchEnabled", False)
    functions_enabled = tools_state.get("functionsEnabled", False)
    code_interpreter_enabled = tools_state.get("codeInterpreterEnabled", False)
    vector_store = tools_state.get("vectorStore")
    web_search_config = tools_state.get("webSearchConfig", {})
    mcp_enabled = tools_state.get("mcpEnabled", False)
    mcp_config = tools_state.get("mcpConfig", {})
    google_integration_enabled = tools_state.get("googleIntegrationEnabled", False)
    
    tools = []
    
    if web_search_enabled:
        web_search_tool: Dict[str, Any] = {"type": "web_search"}
        user_location = web_search_config.get("user_location")
        if user_location and (
            user_location.get("country") != ""
            or user_location.get("region") != ""
            or user_location.get("city") != ""
        ):
            web_search_tool["user_location"] = user_location
        tools.append(web_search_tool)
    
    if file_search_enabled:
        file_search_tool = {
            "type": "file_search",
            "vector_store_ids": [vector_store.get("id")] if vector_store else [],
        }
        tools.append(file_search_tool)
    
    if code_interpreter_enabled:
        tools.append({"type": "code_interpreter", "container": {"type": "auto"}})
    
    if functions_enabled:
        for tool in tools_list:
            tools.append({
                "type": "function",
                "name": tool["name"],
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": tool["parameters"],
                    "required": list(tool["parameters"].keys()),
                    "additionalProperties": False,
                },
                "strict": True,
            })
    
    if mcp_enabled and mcp_config.get("server_url") and mcp_config.get("server_label"):
        mcp_tool: Dict[str, Any] = {
            "type": "mcp",
            "server_label": mcp_config["server_label"],
            "server_url": mcp_config["server_url"],
        }
        if mcp_config.get("skip_approval"):
            mcp_tool["require_approval"] = "never"
        if mcp_config.get("allowed_tools", "").strip():
            mcp_tool["allowed_tools"] = [
                t.strip()
                for t in mcp_config["allowed_tools"].split(",")
                if t.strip()
            ]
        tools.append(mcp_tool)
    
    if google_integration_enabled and request:
        from lib.connectors_auth import get_fresh_access_token
        fresh_tokens = await get_fresh_access_token(request)
        if fresh_tokens.accessToken:
            tools.extend(get_google_connector_tools(fresh_tokens.accessToken))
    
    return tools
