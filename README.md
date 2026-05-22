# ShadowReel AI — Production AI Generation SaaS Platform

ShadowReel AI is a production-grade, high-throughput, and VRAM-optimized AI cinematic documentary and image generation platform. It is designed to run at scale, leveraging a decoupled backend/frontend architecture with distributed asynchronous workers, GPU cluster management, and secure media rendering.

The platform is designed to emulate the infrastructure scale and stability of commercial generative platforms like Runway, Luma Dream Machine, and Kling AI.

---

## 🌌 Platform Architecture

ShadowReel AI is engineered as a decoupled, multi-node architecture, separating client-facing web application nodes, stateless API nodes, distributed Celery task queues, and elastic GPU generation workers.

```
                     ┌───────────────────────┐
                     │     Cloudflare Edge   │ (SSL, CDN Caching, WAF)
                     └───────────┬───────────┘
                                 │
                     ┌───────────▼───────────┐
                     │   NGINX Reverse Proxy │ (Port 80/443 Gateway)
                     └─────┬───────────┬─────┘
                           │           │
            ┌──────────────┘           └──────────────┐
            │ / (Frontend Assets)                     │ /api /ws (Backend Traffic)
    ┌───────▼───────────────┐                 ┌───────▼───────────────┐
    │  Next.js 15 (Node)    │                 │  FastAPI API Server   │
    │  (Standalone cluster) │                 │  (Stateless Scale)     │
    └───────────────────────┘                 └───────┬───────────────┘
                                                      │
                       ┌──────────────────────────────┼──────────────────────────────┐
                       │ publish/subscribe            │ database queries             │ enqueue task
             ┌─────────▼─────────┐          ┌─────────▼─────────┐          ┌─────────▼─────────┐
             │    Redis Cache    │          │  PostgreSQL DB    │          │  Celery Message   │
             │   & Rate Limiter  │          │ (Async pgPool)    │          │   Broker (Redis)  │
             └───────────────────┘          └───────────────────┘          └─────────┬─────────┘
                                                                                     │
                                    ┌────────────────────────────────────────────────┤
                                    │ -Q generation (Image worker)                   │ -Q video (GPU worker)
                          ┌─────────▼─────────┐                            ┌─────────▼─────────┐
                          │   Celery Worker   │                            │   Celery Worker   │
                          │   (Image Scale)   │                            │  (GPU/Wan2.1 node)│
                          └─────────┬─────────┘                            └─────────┬─────────┘
                                    │ API / WS                                       │ API / WS
                          ┌─────────▼─────────┐                            ┌─────────▼─────────┐
                          │ ComfyUI (Flux)    │                            │ ComfyUI (Wan2.1)  │
                          │ (VRAM Optimized)  │                            │ (Nvidia GPU Node) │
                          └─────────┬─────────┘                            └─────────┬─────────┘
                                    │ upload                                         │ upload
                                    └───────────────────────┬────────────────────────┘
                                                            ▼
                                                ┌───────────────────────┐
                                                │  S3 Compatible Cloud  │ (AWS S3, Cloudflare R2, MinIO)
                                                │  Storage (Media CDN)  │
                                                └───────────────────────┘
```

### Core Components
1. **Frontend App**: Next.js 15 App Router optimized for standalone deployment, using Tailwind CSS, Framer Motion, and WebSockets.
2. **API Layer**: FastAPI ASGI server handling HTTP REST endpoints, secure file metadata, database orchestrations, and real-time state tracking via WebSockets.
3. **Queue Broker**: Redis 7.0 for managing Celery message transfers, API rate limiting, and real-time job-state caching.
4. **Asynchronous Workers**: Distributed Celery workers segmented by hardware queues:
   - `generation` queue: Standard worker executing FLUX cinematic image pipelines.
   - `video` queue: Dedicated GPU worker with Nvidia runtime bindings executing Wan2.1 video pipelines.
   - `documentary` queue: High-level orchestrator calling AI Director agents and composing audio/video files.
5. **Storage Layer**: AWS S3/Cloudflare R2 compatible object store serving media via CDN edge configurations.
6. **ComfyUI Cluster**: Distributed GPU execution graphs with TAESD VRAM paging, model warm-loading, and workflow caching.

---

## 🛠️ Local Development & Setup

### Prerequisites
* **Docker & Docker Compose** (minimum v2.20.0)
* **Node.js** v20+ and **Python** v3.11+
* **FFmpeg** installed locally (required for video rendering outside Docker)
* **ComfyUI** running locally or on a remote node on port `8188`

### Quick Start (Dev Mode)
1. Clone the repository and navigate to the project directory.
2. Create environment configs from templates:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```
3. Initialize the development environment and boot all services (FastAPI, Next.js, Postgres, Redis, and Celery):
   ```powershell
   # On Windows
   ./start-dev.ps1
   ```
   *This PowerShell script starts Postgres & Redis via Docker, builds the Python virtual environment, registers Celery workers, and hosts the Next.js dev server.*

---

## 🐳 Docker Deployment (Production)

ShadowReel is fully packaged for Docker orchestration, featuring optimized multi-stage images, strict non-root security, and GPU pass-through configurations.

### Production Environment Setup
Before running the container suite, configure `.env.production` at the root directory:
```bash
POSTGRES_USER=shadowreel_prod
POSTGRES_PASSWORD=your_secure_db_password
POSTGRES_DB=shadowreel
REDIS_HOST=redis
COMFYUI_HOST=comfyui-node.internal.net
S3_BUCKET=shadowreel-assets
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
SECRET_KEY=...
```

### Running the Services
Start the full application stack (Nginx, API, Workers, Frontend, Databases, and Flower) using:
```bash
docker compose -f docker-compose.production.yml up --build -d
```

Check the health and logs of the running production containers:
```bash
docker compose -f docker-compose.production.yml ps
docker compose -f docker-compose.production.yml logs -f api
```

---

## 🔒 Production Security Hardening

ShadowReel AI enforces strict enterprise-grade security protocols across all boundary layers:
* **JWT Access Controls**: REST endpoints require signed HS256 JWT validation, validating expiration (`exp`), issue times (`iat`), and user sub-claims.
* **API Rate Limiting**: Redis-backed sliding-window rate limiters block API and generation queues from abuse.
* **Upload Sanitization**: Upload validation processes restrict uploaded files to designated sizes (e.g. 50MB) and verify file MIME magic bytes.
* **CORS & CORS Hardening**: Middleware strictly enforces allowed origins from environment settings.
* **Nginx Gateway**: Nginx isolates the API server, sanitizes headers, secures WebSocket handshakes, and limits request body payloads.

---

## 📈 Distributed Infrastructure Deployments

### RunPod Serverless / Pod Setup
To deploy GPU workers to RunPod:
1. Build the backend Docker image and push it to your private container registry (e.g. DockerHub or AWS ECR):
   ```bash
   docker build -t yourregistry/shadowreel-backend:latest -f backend/Dockerfile ./backend
   docker push yourregistry/shadowreel-backend:latest
   ```
2. Spawn a RunPod GPU Pod (e.g. RTX 4090 or A40) and set the container image to `yourregistry/shadowreel-backend:latest`.
3. Override the default entrypoint to register the Celery GPU worker:
   ```bash
   celery -A workers.celery_app worker -Q video -l info -c 1 --max-tasks-per-child=10 --max-memory-per-child=12000000
   ```

### Vast.ai Deployment
A custom automation script is provided at `deployment/vast/setup.sh`. To initialize a GPU node on Vast.ai:
1. Connect to the Vast.ai instance via SSH.
2. Transfer and run the setup script:
   ```bash
   curl -sSL https://raw.githubusercontent.com/your-repo/shadowreel/main/deployment/vast/setup.sh | bash
   ```
3. Run the worker container with Nvidia runtime capabilities (`--gpus all`) mapped to the Redis broker.

---

## 🚀 CI/CD Pipeline

A production GitHub Actions workflow is located at `.github/workflows/ci.yml`. On every Pull Request or push to main, the CI/CD:
1. Lints the frontend code using ESLint.
2. Checks backend code quality and syntax.
3. Tests Next.js production builds.
4. Verifies Docker image compilation for both backend and frontend.
5. Runs mock validation tests to ensure compilation and integration safety.

---

## 📄 API Specifications

| Method | Endpoint | Payload / Params | Description |
|---|---|---|---|
| `POST` | `/api/v1/generate/image` | `{ prompt, width, height, ... }` | Queue cinematic image generation |
| `POST` | `/api/v1/generate/video` | `{ prompt, image_id, duration, ... }` | Queue temporal-consistent video generation |
| `GET` | `/api/v1/generate/status/{id}` | - | Poll job execution state |
| `GET` | `/api/v1/generate/history` | `?limit=20` | Fetch gallery history items |
| `WS` | `/ws/jobs/{id}` | - | Establish real-time progress stream |
| `GET` | `/health` | - | Return system health metrics (API & ComfyUI) |

---

## 🧑‍💻 License & Authors
ShadowReel AI is private enterprise code. Authorized deployment teams only. For questions or system configurations, contact `ops@shadowreel.ai`.
