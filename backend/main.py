from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os

from api import (
    turn_response,
    google_auth,
    google_callback,
    google_status,
    vector_stores,
    functions,
    container_files,
)

app = FastAPI(title="OpenAI Responses Starter App Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:8501",  # Streamlit default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(turn_response.router, prefix="/api/turn_response", tags=["turn_response"])
app.include_router(google_auth.router, prefix="/api/google/auth", tags=["google"])
app.include_router(google_callback.router, prefix="/api/google/callback", tags=["google"])
app.include_router(google_status.router, prefix="/api/google/status", tags=["google"])
app.include_router(vector_stores.router, prefix="/api/vector_stores", tags=["vector_stores"])
app.include_router(functions.router, prefix="/api/functions", tags=["functions"])
app.include_router(container_files.router, prefix="/api/container_files", tags=["container_files"])


@app.get("/")
async def root():
    return {"message": "OpenAI Responses Starter App Backend"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

