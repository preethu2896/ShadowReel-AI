#!/usr/bin/env bash
# ==============================================================================
# ShadowReel AI — GPU Server Bootstrap Script
# ==============================================================================
# Target OS: Ubuntu 20.04 / 22.04 LTS (Bare-Metal, RunPod, Vast.ai, Lambda Labs)
# Purpose: Installs Docker, Docker Compose, NVIDIA Drivers, and NVIDIA Container 
#          Toolkit to enable GPU pass-through to containers.
# ==============================================================================

set -euo pipefail

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0;60m' # No Color
NC_RESET='\033[0m'

log_info() {
    echo -e "${BLUE}[$(date +'%T')] [INFO] ${1}${NC_RESET}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%T')] [SUCCESS] ${1}${NC_RESET}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%T')] [WARNING] ${1}${NC_RESET}"
}

log_error() {
    echo -e "${RED}[$(date +'%T')] [ERROR] ${1}${NC_RESET}"
}

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run this script as root (sudo)."
    exit 1
fi

log_info "Starting GPU Server Bootstrap for ShadowReel AI..."

# 1. Update package list and upgrade core packages
log_info "Updating package lists..."
apt-get update -y
apt-get upgrade -y

# 2. Install basic system utilities
log_info "Installing basic utilities (curl, wget, git, ffmpeg, build-essential)..."
apt-get install -y curl wget git ffmpeg build-essential software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# 3. Install NVIDIA drivers if not already present
if ! command -v nvidia-smi &> /dev/null; then
    log_warning "nvidia-smi not detected. Installing recommended NVIDIA drivers..."
    ubuntu-drivers install
    log_warning "NVIDIA drivers installed. A reboot is highly recommended before running Docker GPU containers."
else
    log_success "NVIDIA drivers detected: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)"
fi

# 4. Install Docker CE
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker Engine..."
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    log_success "Docker installed successfully."
else
    log_success "Docker already installed: $(docker --version)"
fi

# 5. Install NVIDIA Container Toolkit
if ! dpkg -l | grep -q nvidia-container-toolkit; then
    log_info "Installing NVIDIA Container Toolkit..."
    
    # Configure the repository
    gpgkey="https://nvidia.github.io/libnvidia-container/gpgkey"
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    
    curl -fsSL $gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
      sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
      tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
      
    apt-get update -y
    apt-get install -y nvidia-container-toolkit
    
    # Configure Nvidia runtime in Docker
    log_info "Configuring Docker to use the NVIDIA Container Runtime..."
    nvidia-ctk runtime configure --runtime=docker
    
    # Restart Docker to apply settings
    systemctl restart docker
    log_success "NVIDIA Container Toolkit configured successfully."
else
    log_success "NVIDIA Container Toolkit is already installed."
fi

# 6. Verify GPU Access in Docker
log_info "Verifying GPU accessibility inside Docker container..."
if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    log_success "Verification passed: CUDA container can access host GPUs."
else
    log_warning "Verification failed: Could not run test CUDA container. Make sure NVIDIA drivers are active and reboot if needed."
fi

# 7. Configure Log Rotation for Docker (prevents log bloat on GPU instances)
log_info "Configuring Docker daemon log limits..."
mkdir -p /etc/docker
cat <<EOF > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "3"
  },
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
EOF

# Restart docker to reload configuration
systemctl restart docker

log_success "======================================================================"
log_success "GPU Bootstrap completed successfully!"
log_success "System is ready for ShadowReel AI stack deployment."
log_success "======================================================================"
log_success "Next steps: Run './deployment/setup_comfyui.sh' to install ComfyUI models."
log_success "======================================================================"
