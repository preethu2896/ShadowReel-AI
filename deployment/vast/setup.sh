#!/usr/bin/env bash

# ==============================================================================
# ShadowReel AI — Vast.ai Host Setup Helper Script
# This script initializes a rented bare-metal Vast.ai instance to run GPU docker
# containers, installs the Nvidia Container Toolkit, and configures Docker log rotation.
# ==============================================================================

set -euo pipefail

echo "=== [1/5] Updating host repositories & system dependencies ==="
sudo apt-get update -y
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common

echo "=== [2/5] Installing Docker Engine ==="
if ! command -v docker &> /dev/null; then
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

echo "=== [3/5] Installing NVIDIA Container Toolkit ==="
if ! dpkg -s nvidia-container-toolkit &> /dev/null; then
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
      sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
      sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

    sudo apt-get update -y
    sudo apt-get install -y nvidia-container-toolkit
    
    echo "Configuring NVIDIA Container Toolkit runtime..."
    sudo nvidia-container-toolkit-cli mode configure
    sudo nvidia-ctk runtime configure --runtime=docker
    
    echo "Restarting Docker daemon..."
    sudo systemctl restart docker
    echo "NVIDIA Container Toolkit installed and Docker restarted."
else
    echo "NVIDIA Container Toolkit is already installed."
fi

echo "=== [4/5] Configuring Docker Log Rotation ==="
# Prevents container logs from filling up the disk on high-throughput generation tasks
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
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

echo "Restarting Docker to apply log-rotation and runtime changes..."
sudo systemctl restart docker

echo "=== [5/5] Verifying GPU Pass-through to Docker ==="
if docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "SUCCESS: GPU passthrough verified! docker can access all NVIDIA GPUs."
else
    echo "WARNING: GPU passthrough check failed. Verify Nvidia drivers on host: run 'nvidia-smi'."
fi

echo "=============================================================================="
echo " Vast.ai GPU Host Setup Completed!"
echo " Next Steps:"
echo " 1. Run Docker Compose: 'docker compose -f docker-compose.production.yml up -d'"
echo " 2. Monitor containers: 'docker ps'"
echo "=============================================================================="
