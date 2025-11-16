from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from openai import OpenAI
from lib.tools import get_tools
from lib.config import get_openai_api_key
from config.constants import get_developer_prompt, MODEL

router = APIRouter()


class TurnRequest(BaseModel):
    messages: List[Dict[str, Any]]
    toolsState: Dict[str, Any]


async def generate_stream(messages: List[Dict[str, Any]], tools_state: Dict[str, Any], request: Any):
    """Generate streaming response from OpenAI"""
    tools = await get_tools(tools_state, request)
    
    print("Tools:", tools)
    print("Received messages:", messages)
    
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in secrets or environment variables")
    openai_client = OpenAI(api_key=api_key)
    
    try:
        # OpenAI Python SDK uses sync streaming, but we can wrap it in async
        import asyncio
        events = openai_client.responses.create(
            model=MODEL,
            input=messages,
            instructions=get_developer_prompt(),
            tools=tools,
            stream=True,
            parallel_tool_calls=False,
        )
        
        for event in events:
            # Convert event to dict
            event_dict = event.model_dump() if hasattr(event, 'model_dump') else dict(event)
            event_type = event_dict.get("type", getattr(event, "type", "unknown"))
            
            data = json.dumps({
                "event": event_type,
                "data": event_dict,
            })
            yield f"data: {data}\n\n"
    except Exception as e:
        error_data = json.dumps({
            "error": str(e)
        })
        yield f"data: {error_data}\n\n"


@router.post("")
async def post_turn_response(request: TurnRequest, http_request: Request):
    """Handle turn response with streaming"""
    try:
        return StreamingResponse(
            generate_stream(request.messages, request.toolsState, http_request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

