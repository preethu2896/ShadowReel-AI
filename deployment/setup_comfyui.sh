#!/usr/bin/env bash
# ==============================================================================
# ShadowReel AI — ComfyUI Setup and Model Directory Scaffolding
# ==============================================================================
# Purpose: Clones ComfyUI, builds python virtual environment, installs necessary
#          dependencies, structures model folders, installs mandatory custom nodes
#          (VideoCombine, etc.), and sets up run configurations.
# ==============================================================================

set -euo pipefail

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

TARGET_DIR="${HOME}/comfyui"

log_info "Starting ComfyUI automated production setup..."
log_info "Target directory: ${TARGET_DIR}"

# 1. Clone ComfyUI repository
if [ ! -d "${TARGET_DIR}" ]; then
    log_info "Cloning ComfyUI from repository..."
    git clone https://github.com/comfyanonymous/ComfyUI.git "${TARGET_DIR}"
else
    log_success "ComfyUI already cloned at ${TARGET_DIR}."
fi

cd "${TARGET_DIR}"

# 2. Setup folders structure
log_info "Scaffolding model and workflow directory structures..."
mkdir -p models/checkpoints
mkdir -p models/loras
mkdir -p models/vae
mkdir -p models/unet
mkdir -p models/clip
mkdir -p models/controlnet
mkdir -p input
mkdir -p output
mkdir -p user/workflows

log_success "Folder scaffolding complete."

# 3. Create virtual environment and install dependencies
if [ ! -d "venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

log_info "Installing PyTorch, CUDA support, and ComfyUI requirements..."
./venv/bin/pip install --upgrade pip
# Install PyTorch with CUDA 12.1 or 11.8 support depending on standard GPU environment
./venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

log_info "Installing ComfyUI base dependencies..."
./venv/bin/pip install -r requirements.txt

# 4. Install Custom Nodes
CUSTOM_NODES_DIR="custom_nodes"
log_info "Installing recommended production custom nodes..."

# Install ComfyUI-Manager (Allows easy node management)
if [ ! -d "${CUSTOM_NODES_DIR}/ComfyUI-Manager" ]; then
    log_info "Cloning ComfyUI-Manager..."
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git "${CUSTOM_NODES_DIR}/ComfyUI-Manager"
    ./venv/bin/pip install -r "${CUSTOM_NODES_DIR}/ComfyUI-Manager/requirements.txt"
fi

# Install VideoCombine / ComfyUI-VideoHelperSuite (Crucial for video outputs/Wan2.1)
if [ ! -d "${CUSTOM_NODES_DIR}/ComfyUI-VideoHelperSuite" ]; then
    log_info "Cloning ComfyUI-VideoHelperSuite..."
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git "${CUSTOM_NODES_DIR}/ComfyUI-VideoHelperSuite"
    ./venv/bin/pip install -r "${CUSTOM_NODES_DIR}/ComfyUI-VideoHelperSuite/requirements.txt"
fi

# 5. Create launch scripts
log_info "Creating startup runner scripts..."

# Write high VRAM configuration startup script (Standard GPU pods)
cat <<'EOF' > run_comfyui_high_vram.sh
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
echo "Starting ComfyUI in HIGH-VRAM / Production Mode..."
./venv/bin/python main.py \
    --listen 0.0.0.0 \
    --port 8188 \
    --highvram \
    --fp16-vae \
    --cuda-malloc \
    --preview-method auto
EOF
chmod +x run_comfyui_high_vram.sh

# Write low VRAM/shared worker configuration startup script
cat <<'EOF' > run_comfyui_low_vram.sh
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
echo "Starting ComfyUI in LOW-VRAM / Shared Mode..."
./venv/bin/python main.py \
    --listen 0.0.0.0 \
    --port 8188 \
    --lowvram \
    --fp8_e4m3fn-textenc \
    --fp8_e4m3fn-unet \
    --cuda-malloc
EOF
chmod +x run_comfyui_low_vram.sh

log_success "Startup scripts written: run_comfyui_high_vram.sh, run_comfyui_low_vram.sh"

# 6. Inform user on where models should go
log_info "Model Download Instructions:"
echo -e "======================================================================"
echo -e "To configure FLUX cinematic and Wan2.1 documentary pipelines:"
echo -e "1. Place Flux/Wan2.1 checkpoints in: ${TARGET_DIR}/models/checkpoints/"
echo -e "   e.g. Wan2.1 1.3B / 14B Video checkpoint"
echo -e "2. Place LoRA weights in:             ${TARGET_DIR}/models/loras/"
echo -e "3. Place VAE files in:               ${TARGET_DIR}/models/vae/"
echo -e "4. Start ComfyUI by running:         ./run_comfyui_high_vram.sh"
echo -e "======================================================================"

log_success "ComfyUI setup complete!"
