# ShadowReel AI — Production & Cloud Deployment Guide

This guide outlines the production deployment, repository cleaning, and multi-node GPU orchestration workflow for the ShadowReel AI platform.

---

## 🗺️ Architecture & Deployment Topology

Below is the production-grade network topology. Public requests land on Cloudflare Edge, transit the Nginx SSL Reverse Proxy, and are routed to either the stateless Next.js frontend node or the FastAPI API gateway. High-throughput tasks are processed asynchronously via Redis + Celery workers with dedicated Nvidia GPU resource mappings.

```
                         ┌───────────────────────┐
                         │   Cloudflare Edge CDN │ (SSL, Edge Caching, WAF)
                         └───────────┬───────────┘
                                     │ (Port 443 HTTPS/WSS)
                         ┌───────────▼───────────┐
                         │  Nginx Reverse Proxy  │ (SSL Termination)
                         └─────┬───────────┬─────┘
                               │           │
           (Frontend Traffic)  │           │  (API & WebSockets)
             ┌─────────────────┘           └─────────────────┐
             ▼                                               ▼
┌─────────────────────────┐                     ┌─────────────────────────┐
│ Next.js Standalone      │                     │ FastAPI ASGI Server     │
│ (Vercel / Node Cluster) │                     │ (Stateless Web Gateway) │
└─────────────────────────┘                     └────────────┬────────────┘
                                                             │ (DB & Queue Brokering)
                               ┌─────────────────────────────┼─────────────────────────────┐
                               │                             │                             │
                     ┌─────────▼─────────┐         ┌─────────▼─────────┐         ┌─────────▼─────────┐
                     │    Redis Cache    │         │   PostgreSQL DB   │         │ Celery Brokering  │
                     │  (Rate Limiter)   │         │ (Pg Connection)   │         │ (Redis Broker)    │
                     └───────────────────┘         └───────────────────┘         └─────────┬─────────┘
                                                                                           │
                                  ┌────────────────────────────────────────────────────────┤
                                  │ -Q generation (FLUX)                                   │ -Q video (Wan2.1)
                        ┌─────────▼─────────┐                                    ┌─────────▼─────────┐
                        │   Celery Worker   │                                    │   Celery Worker   │
                        │   (Image Scale)   │                                    │   (GPU Video)     │
                        └─────────┬─────────┘                                    └─────────┬─────────┘
                                  │ API                                                    │ API
                        ┌─────────▼─────────┐                                    ┌─────────▼─────────┐
                        │  ComfyUI Server   │                                    │  ComfyUI Server   │
                        │  (FLUX/VRAM Tuned)│                                    │  (Wan2.1 GPU Node)│
                        └─────────┬─────────┘                                    └─────────┬─────────┘
                                  └──────────────────────────┬─────────────────────────────┘
                                                             │ S3 Uploads
                                                             ▼
                                                ┌─────────────────────────┐
                                                │ S3 Compatible Storage   │ (AWS S3, R2, MinIO)
                                                └─────────────────────────┘
```

---

## 📋 Pre-Deployment Validation Checklist

Before initiating production publishing, execute the automated validation suite to ensure that your local/staging setup has correct dependencies, drivers, and API bindings.

Run the validation script using the local virtual environment:
```bash
python backend/scripts/validate_deployment.py
```

---

## 1. GitHub Publishing & Repository Cleanup

### Staging & Cleanup
We provide a PowerShell script `deploy_git.ps1` at the root directory to clean up runtime caches, pycache directories, local active configuration files, and temporary outputs, stage production-safe files, and prepare the Git tree:

1. Open PowerShell in the root project directory.
2. Run the Git publisher:
   ```powershell
   ./deploy_git.ps1
   ```
3. When prompted, enter your remote repository origin URL to hook up and publish to your GitHub server.

---

## 2. Environment Configuration Matrix

ShadowReel requires configuration variables across three files. Use these templates to set up your environment:

### `.env.production` (Root - Docker Compose)
| Variable | Value/Description |
|---|---|
| `SECRET_KEY` | 32-byte secure HEX string used for signing JWT access tokens. |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | PostgreSQL database admin credentials. |
| `POSTGRES_DB` | Name of the database (e.g. `shadowreel_prod`). |
| `COMFYUI_HOST` | Hostname of the target ComfyUI server instance (default `comfyui`). |
| `S3_BUCKET` / `S3_ACCESS_KEY` / `S3_SECRET_KEY` | S3 bucket credentials for media uploads. |
| `CDN_BASE_URL` | Cloudflare CDN/CloudFront URL mapped to the S3 bucket to serve cached assets fast. |

### `backend/.env` (FastAPI Service)
Copy `backend/.env.example` to `backend/.env` and replace details:
* `USE_SQLITE=false` (forces PostgreSQL engine).
* `USE_FAKE_REDIS=false` (forces production Redis broker).
* Set production database credentials.

### `frontend/.env.local` (Next.js Service)
Copy `frontend/.env.local.example` to `frontend/.env.local`:
* `NEXT_PUBLIC_API_URL=https://api.shadowreel.ai`
* `NEXT_PUBLIC_WS_URL=wss://api.shadowreel.ai`

---

## 3. GPU Server Deployment Automation (RunPod / Vast.ai / Bare-metal)

To set up external GPU workers on nodes running Ubuntu 20.04/22.04:

### Step 1: System Bootstrapping
Clone the repository onto the GPU instance, log in as root, and run the bootstrap script:
```bash
chmod +x deployment/bootstrap_gpu.sh
sudo ./deployment/bootstrap_gpu.sh
```
*This installs system tools, Docker, Docker Compose, NVIDIA drivers, Container Toolkit, and logs rotators.*

### Step 2: ComfyUI & Model Architecture Setup
Run the ComfyUI setup script to clone ComfyUI, install dependencies, and download necessary custom nodes:
```bash
chmod +x deployment/setup_comfyui.sh
./deployment/setup_comfyui.sh
```
*Creates model folders: `models/checkpoints/`, `models/loras/`, `models/vae/`.*

### Step 3: Load Models
Move weights into ComfyUI directories:
* Place **FLUX/Wan2.1** models into `~/comfyui/models/checkpoints/`
* Place **LoRAs** into `~/comfyui/models/loras/`
* Place **VAEs** into `~/comfyui/models/vae/`

### Step 4: Run ComfyUI on GPU Nodes
To start ComfyUI with optimal VRAM limits and external API listening:
* For High VRAM GPUs (A100, RTX 4090):
  ```bash
  cd ~/comfyui
  ./run_comfyui_high_vram.sh
  ```
* For Low/Shared VRAM GPUs (RTX 3060, T4):
  ```bash
  cd ~/comfyui
  ./run_comfyui_low_vram.sh
  ```

---

## 4. Production Service Launch (Docker Compose)

Launch the primary stack (PostgreSQL, Redis, API, Workers, Flower Monitoring) on your main cloud manager:

1. Complete the `.env.production` file.
2. Build and run the docker-compose suite in detached mode:
   ```bash
   docker compose -f docker-compose.production.yml up --build -d
   ```
3. Check system status:
   ```bash
   docker compose -f docker-compose.production.yml ps
   ```
4. Verify Celery workers:
   ```bash
   docker compose -f docker-compose.production.yml logs -f worker_video worker_image
   ```

---

## 5. SSL, Subdomain, & Domain Setup (Nginx)

The production configuration file is prepared at [production_ssl.conf](file:///c:/Users/preet/OneDrive/Desktop/ShadowReel/deployment/nginx/production_ssl.conf).

### Subdomain Routing Strategy:
* `shadowreel.ai` and `www.shadowreel.ai` point to the Next.js frontend container (`frontend:3000`).
* `api.shadowreel.ai` points to the FastAPI ASGI API container (`api:8000`).
* `api.shadowreel.ai/ws/` handles upgraded WebSocket streams.

### Generating Let's Encrypt SSL Certificates:
On the host server, run Certbot to request certificates for the domain:
```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot certonly --standalone -d shadowreel.ai -d www.shadowreel.ai -d api.shadowreel.ai
```
Place certificate references into the default locations:
* `/etc/letsencrypt/live/shadowreel.ai/fullchain.pem`
* `/etc/letsencrypt/live/shadowreel.ai/privkey.pem`

Copy the Nginx configuration:
```bash
cp deployment/nginx/production_ssl.conf /etc/nginx/nginx.conf
sudo systemctl restart nginx
```

---

## 6. Frontend Platform Deployment

### Deploying Next.js on Vercel
Vercel is natively configured using the provided [vercel.json](file:///c:/Users/preet/OneDrive/Desktop/ShadowReel/frontend/vercel.json):

1. Link your repository to Vercel.
2. In Project Settings, set Environment Variables:
   * `NEXT_PUBLIC_API_URL` = `https://api.shadowreel.ai`
   * `NEXT_PUBLIC_WS_URL` = `wss://api.shadowreel.ai`
3. Vercel automatically routes `/api/*` and `/ws/*` calls to the FastAPI gateway based on the `vercel.json` rewrites.

### Deploying on Cloudflare Pages
1. Configure build command: `npm run build`
2. Set Build Output Directory: `.next` or standard Static directory.
3. Configure environment variables in the Cloudflare Dashboard.

---

## 7. Troubleshooting & Recovery Commands

### Celery Workers show "Lost Connection to Redis"
* Ensure the Redis container is healthy:
  ```bash
  docker compose -f docker-compose.production.yml ps redis
  ```
* Restart Redis:
  ```bash
  docker compose -f docker-compose.production.yml restart redis
  ```

### GPU Worker is out of Memory
* The workers in `docker-compose.production.yml` are configured with memory limits:
  * `--max-memory-per-child=12000000` (Recycles worker thread if RAM exceeds 12GB).
* To force recycle:
  ```bash
  docker compose -f docker-compose.production.yml restart worker_video
  ```

### Nginx fails to restart (SSL cert error)
* Check Nginx syntax:
  ```bash
  nginx -t
  ```
* If certificates are missing, create placeholder self-signed certs first to prevent Nginx boot crashes:
  ```bash
  mkdir -p /etc/letsencrypt/live/shadowreel.ai/
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/letsencrypt/live/shadowreel.ai/privkey.pem \
    -out /etc/letsencrypt/live/shadowreel.ai/fullchain.pem
  ```
