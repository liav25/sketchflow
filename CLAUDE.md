# SketchFlow ‒ CLAUDE.md

## Project Overview
- **Name**: SketchFlow  
- **Purpose**: AI‑powered web app to convert hand‑drawn sketches/diagrams into digital diagrams (Mermaid text, Draw.io XML) quickly and accurately.  
- **MVP Focus**: Support for Mermaid and Draw.io export formats only.  

---

## Features & Requirements

### 1. Core Conversion Flow
- Upload or take a photo (mobile) of a hand‑drawn sketch + optional user notes.  
- Agent 1 (Vision‑Language): Analyze sketch & notes → produce structured description.  
- Agent 2: Generate the digital diagram in chosen format (Mermaid / Draw.io).  
- Agent 3: Render the diagram, auto‑validate, suggest and apply corrections.  
- Final output is saved (if user is authenticated) and can be exported/share/distributed.  

### 2. Diagram Formats (MVP)
- **Mermaid**: valid syntax, support flowcharts, sequence diagrams etc.  
- **Draw.io**: XML export compatible with Draw.io.  

---

## Authentication & Access Levels

- **Anonymous / Guest**: Can upload & preview generated diagram. Cannot export, copy code, or permanently save.  
- **Registered User**: Sign up via Google OAuth or email/password. Access to save, export, copy code, share.  
- Saved diagrams stored in personal library/dashboard.  

---

## Usage / Monetization

- First chart conversion is free for each new user.  
- Subsequent conversions cost credits.  
- System for granting credits manually (for testers, friends).  
- Dashboard shows credit balance, usage history.  

---

## Integrations

- Google Drive export / sharing: allow users to send their diagram files (Mermaid / Draw.io / image) into their Google Drive.  
- Storage of uploads & generated files in cloud (e.g., AWS S3 or equivalent).  

---

## Mobile & UX

- Mobile app / mobile web view must support camera integration (take photo).  
- Responsive design: works well on phone, tablet, desktop.  

---

## Security & Privacy

- Uploaded images are deleted after conversion unless the user saves the diagram in their library.  
- Data encryption in transit + at rest.  
- Comply with privacy laws (GDPR or relevant local laws).  
- User can request deletion/export of their data.  

---

## Dashboard / User Interface

- **Landing Page**: upload / take photo → add notes → choose format → convert  
- **Result View**: show preview + code (Mermaid / Draw.io) + export options (if registered)  
- **Library / Dashboard**: list of saved diagrams, usages, share/export features  
- **Account / Settings**: profile, credits, link to Google Drive settings  

---

## Admin Tools

- Manage users, view usage stats, grant credits manually  
- Track conversion accuracy / error rates  
- Analytics: numbers of free vs paid conversions, retention, active users  

---

## Success Metrics

- Time from photo upload → digital diagram ready (target < 30s)  
- Accuracy / user satisfaction (feedback, correction frequency)  
- Number of conversions per user & overall  
- Free → paid conversion ratio  
- Active registered users monthly  

---

## Exclusions / MVP Limitations

- **No** in‑app editing of the diagram beyond conversion + auto‑correction (i.e., users cannot move nodes manually, change layout, etc.).  
- Only Mermaid and Draw.io supported at launch.  
- English language only for MVP.  


## Project Status

**Current Phase**: Phase 3 Complete - Frontend Implementation
- ✅ Architecture design finalized with simple client-server pattern
- ✅ Technology stack aligned: FastAPI + Next.js + Supabase Auth + Render hosting
- ✅ Database schema designed with 5 core tables
- ✅ AI pipeline defined with LangGraph 3-agent workflow
- ✅ File storage strategy: Render persistent storage
- ✅ Configuration approach: Single .env file for all environments
- ✅ Project structure created with backend, frontend, shared directories
- ✅ Docker configuration for local development environment
- ✅ FastAPI backend initialized with modular structure
- ✅ Next.js frontend initialized with TypeScript and Tailwind CSS
- ✅ SQLAlchemy models created for all 5 database tables
- ✅ Alembic configured for database migrations
- ✅ Environment configuration template created
- ✅ JWT authentication middleware implemented for FastAPI
- ✅ Supabase client configuration and API client utilities
- ✅ User profile and credit management endpoints
- ✅ File upload handling with validation and storage
- ✅ Frontend authentication with Google OAuth integration
- ✅ Basic UI components for authentication and sketch upload
- ✅ Database migration system ready
- ✅ Complete development setup documentation
- ✅ Complete frontend application with responsive mobile-first design
- ✅ Sketch upload component with drag & drop and mobile camera support
- ✅ File validation and preview functionality
- ✅ Notes input and format selection (Mermaid/Draw.io)  
- ✅ Mock conversion flow with loading states and progress indicators
- ✅ Diagram preview and export functionality (copy, download, share)
- ✅ Seamless mobile and desktop user experience
- ✅ Complete user flow from upload to final diagram output

**Current Phase**: Phase 4 Complete - Basic Backend Integration
- ✅ FastAPI backend service implementation
- ✅ Single unified `/api/convert` endpoint for both Mermaid and Draw.io formats
- ✅ Basic 3-agent pipeline skeleton (Vision → Generation → Validation)
- ✅ Mock conversion logic with realistic processing delays
- ✅ File upload validation and storage system  
- ✅ Frontend-backend integration with real API calls
- ✅ Error handling and user feedback for failed conversions
- ✅ End-to-end testing with both diagram formats

**Next Phase**: AI Model Integration
- [ ] Replace skeleton agents with real AI model calls
- [ ] Implement vision analysis with GPT-4V or Claude Vision
- [ ] Add advanced diagram generation logic
- [ ] Implement diagram validation and auto-correction
- [ ] Add diagram preview generation capabilities


## Repository Structure

```
sketchflow/
├── README.md - Basic project name only
├── .git/ - Git repository initialization  
├── CLAUDE.md - Project requirements and status (this file)
├── tech_stack.md - Detailed technology stack
├── architecture.md - System architecture and design
├── .env.example - Environment configuration template
├── .gitignore - Git ignore rules
├── docker-compose.yml - Local development environment
├── backend/ - FastAPI backend service
│   ├── Dockerfile - Backend container configuration
│   ├── requirements.txt - Python dependencies
│   ├── alembic.ini - Database migration configuration
│   ├── alembic/ - Database migration scripts
│   └── app/ - Application source code
│       ├── main.py - FastAPI application entry point
│       ├── core/ - Core configuration and utilities
│       ├── db/ - Database connection and session management
│       ├── models/ - SQLAlchemy database models
│       ├── api/ - API endpoints and routing
│       └── services/ - Business logic services
├── frontend/ - Next.js frontend application
│   ├── Dockerfile - Frontend container configuration
│   ├── package.json - Node.js dependencies and scripts
│   ├── next.config.js - Next.js configuration
│   ├── tsconfig.json - TypeScript configuration
│   ├── tailwind.config.js - Tailwind CSS configuration
│   └── src/ - Frontend source code
│       ├── app/ - Next.js App Router pages and layouts
│       ├── components/ - Reusable UI components
│       ├── lib/ - Utility libraries and configurations
│       ├── hooks/ - Custom React hooks
│       └── types/ - TypeScript type definitions
└── shared/ - Shared utilities and types
    ├── types/ - Common TypeScript interfaces
    └── utils/ - Shared utility functions
```

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start
1. **Clone and configure environment:**
   ```bash
   git clone <repository-url>
   cd sketchflow
   cp .env.example .env
   # Edit .env with your Supabase credentials and API keys
   ```

2. **Start with Docker (Recommended):**
   ```bash
   docker-compose up --build
   ```
   This starts:
   - PostgreSQL database on port 5432
   - FastAPI backend on port 8000
   - Next.js frontend on port 3000

3. **Initialize database:**
   ```bash
   # In a new terminal, run database migration
   docker-compose exec backend python migrate.py
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Environment Variables
Copy `.env.example` to `.env` and configure:

**Required for Basic Functionality:**
- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_JWT_SECRET` - Supabase JWT secret
- `NEXT_PUBLIC_SUPABASE_URL` - Same as SUPABASE_URL (for frontend)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Same as SUPABASE_ANON_KEY (for frontend)

**Required for AI Features (Phase 3):**
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key

### Development Workflow

**Backend Development:**
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run locally (with database in Docker)
docker-compose up db
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Development:**
```bash
# Install dependencies
cd frontend
npm install

# Run locally (development server with Turbopack)
npm run dev

# Access the application at http://localhost:3000
# The frontend is fully functional with mock conversion flow
```

**Database Operations:**
```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Reset database (development only)
docker-compose down -v
docker-compose up -d db
docker-compose exec backend python migrate.py
```


## Architecture

See `architecture.md` for complete system design. Key points:
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy 2.x + PostgreSQL  
- **Authentication**: Supabase Auth with JWT verification
- **AI**: LangGraph 3-agent pipeline with LiteLLM provider abstraction
- **Storage**: Render persistent storage for files and previews
- **Deployment**: Render Web Services with Docker containers

# Important Instructions!!!

1. Every time you change or edit something in code, update the project status (in a short phrase) and project architecture in this file (CLAUDE.md)

2. Your design and implementation must ALWAYS be very simple and 

3. DO NOT write redundant files or tests unless you were explicitly requested to.

4. ALWAYS STICK WITH OUR PLAN. If you have questions or offers for improvements, please ask me before implementing.