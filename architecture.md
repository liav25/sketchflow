# SketchFlow Architecture

## Overview
SketchFlow is an AI-powered web application that converts hand-drawn sketches into digital diagrams (Mermaid and Draw.io formats). The architecture follows a simple client-server pattern with Supabase for authentication and Render for hosting.

## System Architecture

```
┌─────────────────┐    JWT     ┌──────────────────┐    SQL    ┌──────────────────┐
│   Next.js       │◄────────── │   FastAPI        │◄───────── │   PostgreSQL     │
│   Frontend      │            │   Backend        │           │   Database       │
│                 │            │                  │           │                  │
│ • React UI      │   HTTPS    │ • API Routes     │  async    │ • User Data      │
│ • Auth State    │◄──────────►│ • AI Orchestration│          │ • Diagrams       │
│ • File Upload   │            │ • File Storage   │           │ • Usage Events   │
└─────────────────┘            └──────────────────┘           └──────────────────┘
         │                               │
         │                               │
         ▼                               ▼
┌─────────────────┐                ┌──────────────────┐
│   Supabase      │                │   AI Providers   │
│   Auth          │                │                  │
│                 │                │ • OpenAI GPT-4V  │
│ • JWT Tokens    │                │ • Anthropic      │
│ • OAuth (Google)│                │   Claude 3       │
│ • User Mgmt     │                │ • LiteLLM Router │
└─────────────────┘                └──────────────────┘
```

## Core Components

### 1. Frontend (Next.js)
- **Technology**: React 18 + Next.js 14 + TypeScript
- **Hosting**: Render Static Site / Node.js service
- **Authentication**: Supabase Auth with JWT tokens
- **State Management**: React Context + TanStack Query
- **Styling**: Tailwind CSS

**Key Features**:
- Responsive design (mobile-first)
- Camera integration for mobile sketch capture
- Real-time conversion status updates
- Anonymous preview vs authenticated user flows

### 2. Backend (FastAPI)
- **Technology**: Python 3.11+ with FastAPI + Uvicorn
- **Hosting**: Render Web Service (Docker container)
- **Database**: Async SQLAlchemy 2.x with PostgreSQL
- **Authentication**: JWT verification against Supabase

**Key Responsibilities**:
- API endpoints for sketch upload and conversion
- AI agent orchestration via LangGraph
- File storage management on Render
- User credit management and validation
- Diagram generation and preview creation

### 3. Database Schema (PostgreSQL)
```sql
-- User profiles (mirrored from Supabase)
users_app (
    id UUID PRIMARY KEY,           -- Supabase user ID
    email VARCHAR NOT NULL,
    credits INTEGER DEFAULT 1,     -- Free first conversion
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Uploaded sketches
sketch (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users_app(id),
    file_path VARCHAR NOT NULL,    -- Render file storage path
    notes TEXT,
    created_at TIMESTAMP
)

-- Conversion jobs (async processing)
conversion_job (
    id UUID PRIMARY KEY,
    sketch_id UUID REFERENCES sketch(id),
    status VARCHAR NOT NULL,       -- pending, processing, completed, failed
    format VARCHAR NOT NULL,       -- mermaid, drawio
    error_message TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
)

-- Generated diagrams
diagram (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES conversion_job(id),
    mermaid_text TEXT,
    drawio_xml TEXT,
    preview_path VARCHAR,          -- Generated preview image
    created_at TIMESTAMP
)

-- Usage tracking
usage_event (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users_app(id),
    credits_used INTEGER NOT NULL,
    event_type VARCHAR NOT NULL,   -- conversion, export
    metadata JSONB,
    created_at TIMESTAMP
)
```

### 4. AI Processing Pipeline (LangGraph)
The conversion process uses a three-agent workflow:

```python
# Agent 1: Vision Analysis
sketch_image + user_notes → structured_description

# Agent 2: Format Generation  
structured_description + target_format → raw_diagram_code

# Agent 3: Validation & Correction
raw_diagram_code → validated_diagram + preview
```

**AI Provider Configuration**:
- Primary: OpenAI GPT-4 Vision (sketch analysis)
- Secondary: Anthropic Claude 3 (text generation)
- Routing: LiteLLM for provider abstraction and fallbacks
- Monitoring: LangSmith for tracing and evaluation

### 5. File Storage
- **Location**: Render persistent storage volumes
- **Structure**:
  ```
  /app/storage/
  ├── uploads/          # Original sketch images
  ├── previews/         # Generated diagram previews
  └── temp/            # Temporary processing files
  ```
- **Cleanup**: Automated cleanup of temp files and old uploads

## Authentication Flow

1. **User Registration/Login**:
   - Frontend uses Supabase Auth (email/password or Google OAuth)
   - Supabase returns JWT access token
   - Frontend stores token in secure HTTP-only cookies

2. **API Authentication**:
   - Every backend request includes JWT in Authorization header
   - FastAPI middleware verifies JWT against Supabase JWKS
   - User identity extracted from JWT `sub` claim

3. **Anonymous Users**:
   - Can upload and preview diagrams
   - Cannot export, save, or access full features
   - Conversion limited to one per session

## Deployment Architecture

### Development Environment
```
Local Machine:
├── Backend: FastAPI dev server (localhost:8000)
├── Frontend: Next.js dev server (localhost:3000)  
├── Database: PostgreSQL in Docker
└── Configuration: Single .env file
```

### Production Environment (Render)
```
Render Services:
├── Web Service (FastAPI): Docker container, auto-scaling
├── Static Site (Next.js): CDN-optimized
├── PostgreSQL: Managed database service
└── Environment Variables: Secure secret management
```

## Configuration Management

**Single `.env` file for all environments**:
```bash
# Database
DATABASE_URL=postgresql://...

# Supabase Auth
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_JWT_SECRET=...

# AI Providers
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
LITELLM_LOG=INFO

# Application
APP_ENV=development|production
ALLOWED_ORIGINS=http://localhost:3000,https://sketchflow.onrender.com
MAX_FILE_SIZE_MB=10
CLEANUP_INTERVAL_HOURS=24

# Observability
SENTRY_DSN=...
LANGSMITH_API_KEY=...
```

## Security Considerations

1. **Authentication**: JWT verification with proper audience/issuer validation
2. **File Upload**: Size limits, type validation, secure filename handling
3. **CORS**: Strict origin validation for API endpoints
4. **Data Privacy**: Automatic cleanup of uploaded files
5. **Rate Limiting**: Credit-based usage control
6. **Secrets**: Environment variable management via Render

## Observability & Monitoring

1. **Error Tracking**: Sentry for both frontend and backend errors
2. **AI Monitoring**: LangSmith for agent pipeline tracing
3. **Performance**: Render built-in metrics and logs
4. **User Analytics**: Basic conversion tracking in database
5. **Health Checks**: `/healthz` endpoint for service monitoring

## Cost Optimization

1. **AI Costs**: Pay-per-use model with LiteLLM cost tracking
2. **Hosting**: Render's efficient container scaling
3. **Storage**: Automated cleanup of temporary files
4. **Database**: Optimized queries and connection pooling
5. **CDN**: Next.js static optimization for frontend assets

## Scalability Considerations

**MVP Phase** (Current):
- Single FastAPI service
- Synchronous diagram generation
- Local file storage on Render

**Future Enhancements**:
- Async job processing with Redis/Celery
- Cloud storage migration (S3)
- Microservice decomposition if needed
- CDN for generated diagrams

## Development Workflow

1. **Local Development**: Docker Compose for full stack
2. **Version Control**: Git with feature branches
3. **CI/CD**: Render auto-deployment on main branch push
4. **Database Migrations**: Alembic with manual approval for production
5. **Testing**: Unit tests for critical paths, integration tests for API endpoints

This architecture prioritizes simplicity and cost-effectiveness while maintaining the flexibility to scale as the product grows.