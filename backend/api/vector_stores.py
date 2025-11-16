from fastapi import APIRouter, Query, Request, Body
from pydantic import BaseModel, model_validator
from typing import Optional
from openai import OpenAI
from lib.config import get_openai_api_key

router = APIRouter()

# Initialize OpenAI client with API key from secrets
api_key = get_openai_api_key()
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in secrets or environment variables")
openai_client = OpenAI(api_key=api_key)


class CreateStoreRequest(BaseModel):
    name: Optional[str] = None
    storeName: Optional[str] = None  # For backward compatibility
    
    @model_validator(mode='before')
    @classmethod
    def validate_request(cls, data):
        if isinstance(data, dict):
            # Accept both 'name' and 'storeName'
            name = data.get('name') or data.get('storeName') or "Untitled"
            return {'name': name}
        return data


class AddFileRequest(BaseModel):
    vectorStoreId: str
    fileId: str


class UploadFileRequest(BaseModel):
    fileObject: dict  # Contains 'name' and 'content' (base64)


@router.post("/create_store")
async def create_store(request: CreateStoreRequest):
    """Create a new vector store"""
    try:
        vector_store = openai_client.vector_stores.create(name=request.name)
        return vector_store.model_dump() if hasattr(vector_store, 'model_dump') else dict(vector_store)
    except Exception as e:
        print(f"Error creating vector store: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Error creating vector store"},
            status_code=500
        )


@router.get("/list_files")
async def list_files(vector_store_id: str = Query(..., alias="vector_store_id")):
    """List files in a vector store"""
    try:
        files = openai_client.vector_stores.files.list(vector_store_id)
        return files.model_dump() if hasattr(files, 'model_dump') else dict(files)
    except Exception as e:
        print(f"Error fetching files: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Error fetching files"},
            status_code=500
        )


@router.get("/retrieve_store")
async def retrieve_store(vector_store_id: str = Query(..., alias="vector_store_id")):
    """Retrieve a vector store"""
    try:
        vector_store = openai_client.vector_stores.retrieve(vector_store_id)
        return vector_store.model_dump() if hasattr(vector_store, 'model_dump') else dict(vector_store)
    except Exception as e:
        print(f"Error fetching vector store: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Error fetching vector store"},
            status_code=500
        )


@router.post("/add_file")
async def add_file(request: AddFileRequest):
    """Add a file to a vector store"""
    try:
        vector_store_file = openai_client.vector_stores.files.create(
            request.vectorStoreId,
            file_id=request.fileId,
        )
        return vector_store_file.model_dump() if hasattr(vector_store_file, 'model_dump') else dict(vector_store_file)
    except Exception as e:
        print(f"Error adding file: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Error adding file"},
            status_code=500
        )


@router.post("/upload_file")
async def upload_file(request: UploadFileRequest):
    """Upload a file to OpenAI"""
    try:
        import base64
        from io import BytesIO
        
        file_buffer = base64.b64decode(request.fileObject["content"])
        file_name = request.fileObject["name"]
        
        # Create a file-like object
        file_obj = BytesIO(file_buffer)
        file_obj.name = file_name
        
        file = openai_client.files.create(
            file=file_obj,
            purpose="assistants",
        )
        return file.model_dump() if hasattr(file, 'model_dump') else dict(file)
    except Exception as e:
        print(f"Error uploading file: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Error uploading file"},
            status_code=500
        )

