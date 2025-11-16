from fastapi import APIRouter, Query
from fastapi.responses import Response
import httpx
from lib.config import get_openai_api_key

router = APIRouter()


@router.get("/content")
async def get_container_file_content(
    file_id: str = Query(..., alias="file_id"),
    container_id: str = Query(None, alias="container_id"),
    filename: str = Query(None),
):
    """Get container file content"""
    if not file_id:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Missing file_id"},
            status_code=400
        )
    
    try:
        url = (
            f"https://api.openai.com/v1/containers/{container_id}/files/{file_id}/content"
            if container_id
            else f"https://api.openai.com/v1/container-files/{file_id}/content"
        )
        
        api_key = get_openai_api_key()
        if not api_key:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content={"error": "OPENAI_API_KEY not found"},
                status_code=500
            )
        
        async with httpx.AsyncClient() as client:
            res = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
            )
            res.raise_for_status()
            
            content_type = res.headers.get("Content-Type", "application/octet-stream")
            content_disposition = f"attachment; filename={filename or file_id}"
            
            return Response(
                content=res.content,
                media_type=content_type,
                headers={"Content-Disposition": content_disposition},
            )
    except Exception as e:
        print(f"Error fetching container file: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Failed to fetch file"},
            status_code=500
        )

