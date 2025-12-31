# Use specific version of nvidia cuda image
FROM wlsdml1114/multitalk-base:1.4 as runtime

# Install dependencies for model download (using --no-cache-dir to save space)
RUN pip install --no-cache-dir -U "huggingface_hub[hf_transfer]" runpod websocket-client

WORKDIR /

# Clone ComfyUI and install requirements in one layer
RUN git clone --depth=1 https://github.com/comfyanonymous/ComfyUI.git && \
    cd /ComfyUI && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /ComfyUI/.git

# Clone and install all custom nodes in one layer to reduce image size
RUN cd /ComfyUI/custom_nodes && \
    # ComfyUI-Manager
    git clone --depth=1 https://github.com/Comfy-Org/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf .git && \
    cd .. && \
    # ComfyUI-GGUF
    git clone --depth=1 https://github.com/city96/ComfyUI-GGUF && \
    cd ComfyUI-GGUF && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf .git && \
    cd .. && \
    # ComfyUI-KJNodes
    git clone --depth=1 https://github.com/kijai/ComfyUI-KJNodes && \
    cd ComfyUI-KJNodes && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf .git && \
    cd .. && \
    # ComfyUI-VideoHelperSuite
    git clone --depth=1 https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite && \
    cd ComfyUI-VideoHelperSuite && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf .git && \
    cd .. && \
    # ComfyUI-GGUF-FantasyTalking
    git clone --depth=1 https://github.com/kael558/ComfyUI-GGUF-FantasyTalking && \
    cd ComfyUI-GGUF-FantasyTalking && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf .git && \
    cd .. && \
    # ComfyUI-wanBlockswap
    git clone --depth=1 https://github.com/orssorbit/ComfyUI-wanBlockswap && \
    cd ComfyUI-wanBlockswap && \
    rm -rf .git && \
    cd .. && \
    # ComfyUI-WanVideoWrapper
    git clone --depth=1 https://github.com/kijai/ComfyUI-WanVideoWrapper && \
    cd ComfyUI-WanVideoWrapper && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf .git && \
    cd .. && \
    # Final cleanup
    find /ComfyUI/custom_nodes -type f -name "*.pyc" -delete && \
    find /ComfyUI/custom_nodes -type d -name "__pycache__" -delete && \
    find /ComfyUI/custom_nodes -type d -name ".git" -exec rm -rf {} + 2>/dev/null || true

# Create model directories (models will be loaded from Network Volume)
RUN mkdir -p /ComfyUI/models/vae/split_files/vae && \
    mkdir -p /ComfyUI/models/text_encoders && \
    mkdir -p /ComfyUI/models/diffusion_models/NSFW && \
    mkdir -p /ComfyUI/models/loras

# Note: All models should be uploaded to RunPod Network Volume
# This approach makes the Docker image much smaller and faster to build
# See DEPLOYMENT_GUIDE.md for model upload instructions

RUN echo "========================================" && \
    echo "📦 Docker镜像构建完成！" && \
    echo "" && \
    echo "⚠️  重要：需要上传以下模型到 RunPod Network Volume" && \
    echo "" && \
    echo "VAE 模型:" && \
    echo "  /runpod-volume/vae/split_files/vae/wan_2.1_vae.safetensors" && \
    echo "" && \
    echo "CLIP 模型:" && \
    echo "  /runpod-volume/text_encoders/nsfw_wan_umt5-xxl_fp8_scaled.safetensors" && \
    echo "" && \
    echo "UNET 模型:" && \
    echo "  /runpod-volume/models/NSFW/Wan2.2_Remix_NSFW_i2v_14b_high_lighting_v2.0.safetensors" && \
    echo "  /runpod-volume/models/NSFW/Wan2.2_Remix_NSFW_i2v_14b_low_lighting_v2.0.safetensors" && \
    echo "" && \
    echo "LoRA 模型 (可选):" && \
    echo "  /runpod-volume/loras/DR34ML4Y_I2V_14B_HIGH.safetensors" && \
    echo "  /runpod-volume/loras/DR34ML4Y_I2V_14B_LOW.safetensors" && \
    echo "  /runpod-volume/loras/... (其他LoRA)" && \
    echo "" && \
    echo "详细说明请查看 DEPLOYMENT_GUIDE.md" && \
    echo "========================================"

COPY . .
COPY extra_model_paths.yaml /ComfyUI/extra_model_paths.yaml
COPY workflow_nsfw.json /workflow_nsfw.json
RUN chmod +x /entrypoint.sh

# Use the NSFW workflow handler by default
# To use the original handler, set ENV HANDLER_FILE=handler.py
ENV HANDLER_FILE=handler_nsfw.py

CMD ["/entrypoint.sh"]