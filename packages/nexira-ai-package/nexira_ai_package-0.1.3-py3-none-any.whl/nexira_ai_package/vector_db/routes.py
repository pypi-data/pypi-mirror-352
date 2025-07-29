from fastapi import APIRouter, HTTPException, FastAPI, UploadFile, File, Form
from .memory_handler import MemoryHandler
from contextlib import asynccontextmanager
import json

qdrant_db_client = MemoryHandler("vector_db")

router = APIRouter(
    prefix="/vector_db",
    tags=["vector_db"]
)

@router.post("/insert_document")
async def insert_document(file: UploadFile = File(...), file_name: str = Form(...), metadata: str = Form(...)):
    try:
        metadata_dict = json.loads(metadata)
        file_bytes = await file.read()
        qdrant_db_client.insert_document(file_bytes, file_name, metadata_dict)
        return {"message": "Document inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

