# tech_stack.md — SketchFlow (Auth via Supabase)

Audience: software engineers (Claude)

This is the authoritative tech stack for SketchFlow, reflecting our decision to use **Supabase Auth** and keep our backend/frontend on **Render**.

---

## 1) Languages & Core Frameworks

- **Backend:** Python 3.11+ with **FastAPI** (ASGI) for HTTP APIs and orchestration.
- **Frontend:** TypeScript with **React + Next.js** (hybrid SSG/SSR).
- **Database:** **PostgreSQL** (Render Managed Postgres).
- **Containerization:** Dockerfile for backend service.

---

## 2) Hosting & Runtime

- **Backend:** Render Web Service (always-on) running FastAPI (`/healthz` endpoint for probes).
- **Frontend:** Next.js app hosted on Render (static or Node server for SSR as needed).
- **Database:** Render Managed Postgres (primary app data).
- **Files:** Render persistent storage via backend endpoints. Previews generated server-side.
 - **Auth** Using Supabase Auth
---

## 3) Authentication (Supabase)

- **Provider:** **Supabase Auth** (GoTrue) — JWT-based user management and OAuth flows. :contentReference[oaicite:0]{index=0}
- **Frontend SDKs:** `@supabase/supabase-js` + `@supabase/ssr` for Next.js server/client auth handling (App Router guidance). :contentReference[oaicite:1]{index=1}
- **Token Format:** Access tokens are JWTs; verify via project JWKS (`/auth/v1/.well-known/jwks.json`) in the backend. :contentReference[oaicite:2]{index=2}
- **Optional:** Anonymous sign-ins for preview flows (can be linked later). :contentReference[oaicite:3]{index=3}

---

## 4) Frontend Integration (Next.js)

- **Packages:** `@supabase/supabase-js`, `@supabase/ssr`.
- **Patterns:**
  - Server-side client for authenticated Server Components / Route Handlers; client-side for UI state. :contentReference[oaicite:5]{index=5}
  - Store session via cookies (Next.js App Router pattern). 
  - On auth events, pass the Supabase-issued JWT with API calls to our FastAPI backend (Bearer).

- **UI:**
  - Email/password and Google OAuth flows.
  - Upload component: `<input type="file" accept="image/*" capture="environment">` for mobile.

---

## 5) Backend Auth Verification (FastAPI)

- **Flow:** Backend receives Supabase JWT (Bearer). Verifies signature against Supabase **JWKS** and validates claims (issuer, audience, expiry). :contentReference[oaicite:6]{index=6}
- **Libs:** `python-jose` or `PyJWT` + JWKS fetching; dependency-injected auth guard for protected routes (patterns similar to standard FastAPI JWT auth). :contentReference[oaicite:7]{index=7}
- **User Identity:** Use `sub` (Supabase user id) as the canonical foreign key for user-owned records on Render Postgres.

> Reference implementations of FastAPI + Supabase Auth exist and follow this approach of validating Supabase JWTs in Python. :contentReference[oaicite:8]{index=8}

---

## 6) Data Model & Persistence

- **ORM:** SQLAlchemy 2.x (async) + Alembic; `asyncpg` driver.
- **Core tables:** `users_app` (profile mirror of Supabase user), `sketch`, `conversion_job`, `diagram`, `usage_event`.
- **Binary outputs:** Mermaid text + Draw.io XML stored as text; previews generated server-side and cached.

> If we later adopt Supabase DB, we can leverage RLS with `auth.uid()` policies directly in Postgres for browser-to-DB access. Not needed now, but noted for future. :contentReference[oaicite:9]{index=9}

---

## 7) AI & Agent Orchestration

- **Agent Graph:** **LangGraph** for multi-step workflow:
  1) Vision+notes → structured description
  2) Description → Mermaid / Draw.io
  3) Render → self-critique → corrections
  4) Finalize/export

- **LLM Abstraction:** **LiteLLM** to route calls to OpenAI/Anthropic with retries/fallbacks.
- **Tracing/Eval:** **LangSmith** for per-run traces and evaluations.

*(docs referenced previously; this section lists the chosen libraries)*

---

## 8) Diagram Tooling

- **Mermaid:** Generate canonical text; server-side preview via `@mermaid-js/mermaid-cli` (PNG/SVG).
- **Draw.io:** Generate compliant XML (stored as text) and static preview.

---

## 9) Observability

- **Backend:** Sentry (errors + traces) + OpenTelemetry auto-instrumentation for FastAPI/HTTP. :contentReference[oaicite:10]{index=10}
- **Agents:** LangSmith traces (inputs/outputs, timings).
- **Platform:** Render logs/metrics dashboards for web service + DB.

---

## 10) Backend Libraries

- FastAPI, Uvicorn
- SQLAlchemy 2.x (async), Alembic, asyncpg
- Pydantic
- httpx (LLM calls via LiteLLM)
- PyJWT / python-jose (JWT), argon2-cffi (only if we add local password flows independent of Supabase)
- tenacity (retries)
- Pillow/OpenCV (preprocessing)
- Sentry SDK; OpenTelemetry (`opentelemetry-instrumentation-fastapi`, OTLP exporter)
- LangGraph, LangSmith, LiteLLM

---

## 11) Frontend Libraries

- React, Next.js, TypeScript
- Tailwind CSS (UI)
- TanStack Query (data fetching/caching)
- `@supabase/supabase-js`, `@supabase/ssr` (auth) :contentReference[oaicite:11]{index=11}
- Minimal components (Headless UI / shadcn) for forms/modals

---

## 12) Build, Deploy, CI/CD

- **Backend:** Docker build → Render Web Service; auto-deploy on main; `/healthz` for probes.
- **Frontend:** Next.js build → Render; PR previews enabled.
- **DB:** Render Managed Postgres; Alembic migrations in CI (manual approval for prod).

---

## 13) Security & Secrets

- **Configuration:** Single .env file for all settings (local dev + Render environment variables).
- **JWT validation:** Enforce issuer/audience/expiry; rotate JWKS cache.
- **CORS/Headers:** Strict CORS; security headers; CSRF for browser flows as applicable.
- **Uploads:** Validate size/type; sanitize filenames; signed download paths when exposed.

