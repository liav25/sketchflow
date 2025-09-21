from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal
import os
import uuid
from datetime import datetime

from app.core.config import settings
from app.core.db import engine, Base, SessionLocal
from app.models.request_log import RequestLog
from app.models.feedback import Feedback
from app.services.conversion import ConversionService
from app.core.logging_config import configure_logging, get_logger
from app.core.auth import get_current_user, get_current_user_optional
from app.services.result_store import save_result, load_result, ConversionRecord
from starlette.middleware.base import BaseHTTPMiddleware

configure_logging()
logger = get_logger("sketchflow.app")

app = FastAPI(title=settings.app_name, debug=settings.debug)


# Database: create tables on startup (simple bootstrap; replace with Alembic later)
@app.on_event("startup")
async def on_startup_create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        get_logger("sketchflow.db").info("Database tables ensured (create_all)")
    except Exception:
        get_logger("sketchflow.db").exception("Failed to create database tables on startup")

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

        # Persist comprehensive request log asynchronously to the database
        try:
            import asyncio
            from app.core.db import SessionLocal

            # Capture response data if available
            response_data = getattr(request.state, "response_data", None)

            async def _persist():
                try:
                    async with SessionLocal() as session:
                        await _save_request_log(session=session,
                                                 method=request.method,
                                                 path=request.url.path,
                                                 status_code=response.status_code,
                                                 duration_ms=duration_ms,
                                                 request=request,
                                                 error=None,
                                                 response_data=response_data)
                except Exception as e:
                    get_logger("sketchflow.request").error(f"Failed to persist request log: {e}")

            # Create the task without awaiting to avoid blocking the response
            task = asyncio.create_task(_persist())
            # Don't await the task, just let it run in background
            
        except Exception as e:
            get_logger("sketchflow.request").error(f"Failed to schedule request log persistence: {e}")

        return response
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        get_logger("sketchflow.request").exception(
            f"Unhandled error for {request.method} {request.url.path} after {duration_ms}ms: {e}"
        )
        # Attempt to persist error case as well
        try:
            import asyncio
            from app.core.db import SessionLocal
            response_data = {"error": str(e), "error_type": type(e).__name__}
            
            async def _persist_error():
                try:
                    async with SessionLocal() as session:
                        await _save_request_log(session=session,
                                                 method=request.method,
                                                 path=request.url.path,
                                                 status_code=500,
                                                 duration_ms=duration_ms,
                                                 request=request,
                                                 error=str(e)[:500],
                                                 response_data=response_data)
                except Exception as persist_error:
                    get_logger("sketchflow.request").error(f"Failed to persist error log: {persist_error}")
                    
            asyncio.create_task(_persist_error())
        except Exception:
            pass
        raise


async def _save_request_log(
    *,
    session,
    method: str,
    path: str,
    status_code: int,
    duration_ms: int,
    request: Request,
    error: str | None,
    response_data: dict | None = None,
):
    try:
        # Collect context set by endpoints
        job_id = getattr(request.state, "job_id", None)
        user_id = getattr(request.state, "user_id", None)
        fmt = getattr(request.state, "format", None)
        notes = getattr(request.state, "notes", None)
        file_info = getattr(request.state, "file_info", {})
        
        # User and network context
        client_ip = request.headers.get("x-forwarded-for") or request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Build comprehensive request data
        request_data = {
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": getattr(request, "path_params", {}),
            "request_id": request.headers.get("x-request-id"),
            "content_length": int(request.headers.get("content-length") or 0),
            "cookies": dict(request.cookies),
        }
        
        # File upload information if available
        if file_info:
            request_data["file_upload"] = file_info
        
        # Conversion parameters if available
        if fmt:
            request_data["conversion"] = {
                "format": fmt,
                "notes": notes,
                "job_id": job_id,
            }
        
        # Additional context for analysis
        extra = {
            "endpoint": path,
            "has_file_upload": bool(file_info),
            "is_conversion_request": path.startswith("/api/convert"),
            "user_authenticated": bool(user_id),
        }

        log = RequestLog(
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            job_id=job_id,
            user_id=user_id,
            format=fmt,
            client_ip=client_ip,
            user_agent=user_agent,
            file_name=file_info.get("filename") if file_info else None,
            file_size=file_info.get("size") if file_info else None,
            file_type=file_info.get("content_type") if file_info else None,
            notes=notes,
            error=error,
            request_data=request_data,
            response_data=response_data,
            extra=extra,
        )
        session.add(log)
        await session.commit()
    except Exception:
        get_logger("sketchflow.request").exception("Failed to persist RequestLog")


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


class FeedbackRequest(BaseModel):
    feedback_text: str


class FeedbackResponse(BaseModel):
    id: int
    message: str


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
    request: Request = None,
):
    # Capture file information for logging
    file_content = await file.read()
    file_size = len(file_content)
    file_info = {
        "filename": file.filename,
        "size": file_size,
        "content_type": file.content_type,
        "size_mb": round(file_size / (1024 * 1024), 2),
    }
    
    # Dev mode: skip file type/size validation to avoid friction
    if not dev_mode:
        if file.content_type not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.allowed_file_types)}",
            )

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
            
            # Attach response data for logging middleware (mock mode)
            if request is not None:
                try:
                    request.state.response_data = {
                        "job_id": job_id,
                        "status": "completed",
                        "result": result,
                        "conversion_successful": True,
                        "mock_mode": True,
                        "result_type": format,
                        "code_length": len(result.get("code", "")) if result and result.get("code") else 0,
                    }
                except Exception:
                    pass
                    
            return ConversionResponse(job_id=job_id, status="completed", result=result)
        
        # Save uploaded file
        upload_dir = os.path.join(settings.storage_path, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        file_path = os.path.join(upload_dir, f"{job_id}{file_extension}")
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Attach context for logging middleware
        if request is not None:
            try:
                request.state.job_id = job_id
                request.state.user_id = (current_user or {}).get("id") if current_user else None
                request.state.format = format
                request.state.notes = notes
                request.state.file_info = file_info
            except Exception:
                pass

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

        # Prepare response data for logging
        response_obj = ConversionResponse(
            job_id=job_id,
            status="completed",
            result=result
        )
        
        # Attach response data for logging middleware
        if request is not None:
            try:
                request.state.response_data = {
                    "job_id": job_id,
                    "status": "completed",
                    "result": result,
                    "conversion_successful": True,
                    "result_type": result.get("format", format) if result else None,
                    "code_length": len(result.get("code", "")) if result and result.get("code") else 0,
                }
            except Exception:
                pass
        
        return response_obj
        
    except Exception as e:
        error_job_id = job_id if 'job_id' in locals() else str(uuid.uuid4())
        
        # Attach error response data for logging middleware
        if request is not None:
            try:
                request.state.response_data = {
                    "job_id": error_job_id,
                    "status": "failed",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "conversion_successful": False,
                }
            except Exception:
                pass
        
        return ConversionResponse(
            job_id=error_job_id,
            status="failed",
            error=str(e)
        )


@app.get("/api/conversions/{job_id}/code", response_model=CodeResponse)
async def get_conversion_code(job_id: str, user=Depends(get_current_user_optional)):
    """Return diagram code for a conversion job. Authentication optional.

    Anonymous users can now retrieve code without signing in.
    """
    item = load_result(job_id)
    if not item:
        raise HTTPException(status_code=404, detail="Job not found")
    return CodeResponse(job_id=job_id, format=item.get("format", "mermaid"), code=item.get("code", ""))


@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    request: Request,
    current_user=Depends(get_current_user_optional),
):
    """Submit feedback from users. Works for both authenticated and anonymous users."""
    try:
        # Get client IP and user agent
        client_ip = request.headers.get("x-forwarded-for") or request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        user_id = (current_user or {}).get("id") if current_user else None
        
        # Create feedback record
        async with SessionLocal() as session:
            feedback_record = Feedback(
                client_ip=client_ip,
                user_id=user_id,
                feedback_text=feedback.feedback_text,
                user_agent=user_agent,
            )
            session.add(feedback_record)
            await session.commit()
            await session.refresh(feedback_record)
            
            return FeedbackResponse(
                id=feedback_record.id,
                message="Thank you for your feedback!"
            )
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
