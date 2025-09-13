from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal
import os
import uuid
from datetime import datetime

from app.core.config import settings
from app.services.conversion import ConversionService

app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS middleware (dev-friendly): allow-all when DEBUG is true
dev_mode = bool(settings.debug)
if dev_mode:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # allow "*" origins
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    origins = (
        settings.allowed_origins
        if isinstance(settings.allowed_origins, list)
        else [settings.allowed_origins]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize conversion service
conversion_service = ConversionService()


class ConversionResponse(BaseModel):
    job_id: str
    status: Literal["completed", "processing", "failed"]
    result: dict | None = None
    error: str | None = None


@app.get("/")
async def root():
    return {"message": "SketchFlow API", "version": "1.0.0"}


@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/convert", response_model=ConversionResponse)
async def convert_sketch(
    file: UploadFile = File(...),
    format: Literal["mermaid", "drawio"] = Form(...),
    notes: str = Form(""),
):
    # Dev mode: skip file type/size validation to avoid friction
    file_content = await file.read()
    if not dev_mode:
        if file.content_type not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.allowed_file_types)}",
            )

        file_size = len(file_content)
        max_size = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
            )

    # Reset file position
    await file.seek(0)
    
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        upload_dir = os.path.join(settings.storage_path, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        file_path = os.path.join(upload_dir, f"{job_id}{file_extension}")
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Process with conversion service
        result = await conversion_service.convert(
            file_path=file_path,
            format=format,
            notes=notes,
            job_id=job_id
        )
        
        return ConversionResponse(
            job_id=job_id,
            status="completed",
            result=result
        )
        
    except Exception as e:
        return ConversionResponse(
            job_id=job_id if 'job_id' in locals() else str(uuid.uuid4()),
            status="failed",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
