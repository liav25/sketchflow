from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal
import os
import uuid
from datetime import datetime

from app.core.config import settings
from app.services.conversion import ConversionService
from app.core.logging_config import configure_logging, get_logger
from app.core.auth import get_current_user, get_current_user_optional
from app.services.result_store import save_result, load_result, ConversionRecord
from starlette.middleware.base import BaseHTTPMiddleware

configure_logging()
logger = get_logger("sketchflow.app")

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
    # Production: parse ALLOWED_ORIGINS from env.
    # Accepts either a JSON array or a comma-separated string.
    raw = settings.allowed_origins
    origins: list[str]
    if isinstance(raw, list):
        origins = raw
    elif isinstance(raw, str):
        val = raw.strip()
        if val.startswith("["):
            try:
                import json
                parsed = json.loads(val)
                origins = parsed if isinstance(parsed, list) else [val]
            except Exception:
                origins = [p.strip() for p in val.split(",") if p.strip()]
        else:
            origins = [p.strip() for p in val.split(",") if p.strip()]
    else:
        origins = []

    # If wildcard is used, disable credentials per CORS rules.
    allow_credentials = True
    if any(o == "*" for o in origins):
        allow_credentials = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Security headers for production (fallback implementation without SecurityMiddleware)
if not dev_mode:
    class AddSecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers.setdefault("X-Frame-Options", "DENY")
            response.headers.setdefault("X-Content-Type-Options", "nosniff")
            response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
            # HSTS for ~6 months
            response.headers.setdefault("Strict-Transport-Security", "max-age=15552000")
            return response

    app.add_middleware(AddSecurityHeadersMiddleware)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start = time.time()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Proceed to handler
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        response.headers["X-Request-ID"] = request_id
        get_logger("sketchflow.request").info(
            f"{request.method} {request.url.path} -> {response.status_code} in {duration_ms}ms",
        )
        return response
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        get_logger("sketchflow.request").exception(
            f"Unhandled error for {request.method} {request.url.path} after {duration_ms}ms: {e}"
        )
        raise


# Initialize conversion service
conversion_service = ConversionService()


class ConversionResponse(BaseModel):
    job_id: str
    status: Literal["completed", "processing", "failed"]
    result: dict | None = None
    error: str | None = None


class CodeResponse(BaseModel):
    job_id: str
    format: str
    code: str


@app.get("/")
async def root():
    return {"message": "SketchFlow API", "version": "1.0.0"}


@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/convert", response_model=ConversionResponse)
async def convert_sketch(
    file: UploadFile = File(...),
    format: Literal["mermaid", "drawio", "uml"] = Form(...),
    notes: str = Form(""),
    mock: bool = Form(False),
    current_user=Depends(get_current_user_optional),
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

        # If mocking is enabled, short-circuit and return synthetic output
        if settings.mock_mode or mock:
            result = await conversion_service.convert(
                file_path="mock://noop",
                format=format,
                notes=notes,
                job_id=job_id,
            )
            return ConversionResponse(job_id=job_id, status="completed", result=result)
        
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
        # Persist result for later retrieval
        try:
            record = ConversionRecord(
                job_id=job_id,
                format=format,
                notes=notes,
                code=result.get("code", ""),
                owner_user_id=(current_user or {}).get("id") if current_user else None,
                created_at=datetime.now().isoformat(),
            )
            save_result(record)
        except Exception:
            get_logger("sketchflow.result_store").exception("Failed to persist conversion result")

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


@app.get("/api/conversions/{job_id}/code", response_model=CodeResponse)
async def get_conversion_code(job_id: str, user=Depends(get_current_user)):
    """Return diagram code for a conversion job. Authentication required.

    This enforces the product rule: only registered users can copy code.
    """
    item = load_result(job_id)
    if not item:
        raise HTTPException(status_code=404, detail="Job not found")
    return CodeResponse(job_id=job_id, format=item.get("format", "mermaid"), code=item.get("code", ""))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
