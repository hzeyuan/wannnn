# NSFW Wan 2.2 RunPod 部署指南

## 📋 项目概述

这是基于你的核心工作流 `video_wan2_2_14B_i2v_api.json` 定制的 RunPod Serverless 部署配置。

## 🎯 使用的模型

### 已自动下载的模型：
1. **VAE**: `split_files/vae/wan_2.1_vae.safetensors` ✅
2. **CLIP**: `nsfw_wan_umt5-xxl_fp8_scaled.safetensors` ✅
3. **LoRA**:
   - `DR34ML4Y_I2V_14B_HIGH.safetensors` ✅
   - `DR34ML4Y_I2V_14B_LOW.safetensors` ✅

### ⚠️ 需要手动上传的模型：
你需要将以下 NSFW Remix 模型上传到 RunPod Network Volume：

**路径**: `/runpod-volume/models/NSFW/`

**文件**:
- `Wan2.2_Remix_NSFW_i2v_14b_high_lighting_v2.0.safetensors`
- `Wan2.2_Remix_NSFW_i2v_14b_low_lighting_v2.0.safetensors`

## 🚀 部署步骤

### 1️⃣ 构建 Docker 镜像

```bash
cd /Users/hzy/Code/zhuilai/runpod_wan2.2/wan22_Runpod_hub

# 构建镜像
docker build -t yourname/wan22-nsfw:v1 .

# 推送到 Docker Hub
docker push yourname/wan22-nsfw:v1
```

### 2️⃣ 在 RunPod 创建 Network Volume

1. 登录 [RunPod Console](https://console.runpod.io/)
2. 创建 Network Volume (推荐 100GB+)
3. 上传 NSFW Remix 模型到 Network Volume:

```bash
# 上传模型文件到:
/runpod-volume/models/NSFW/Wan2.2_Remix_NSFW_i2v_14b_high_lighting_v2.0.safetensors
/runpod-volume/models/NSFW/Wan2.2_Remix_NSFW_i2v_14b_low_lighting_v2.0.safetensors
```

### 3️⃣ 创建 Serverless Endpoint

1. 在 RunPod Console 创建新的 Serverless Endpoint
2. **Docker Image**: `yourname/wan22-nsfw:v1`
3. **Container Disk**: 180GB
4. **GPU**: 选择 `ADA_24` 或 `ADA_32_PRO`
5. **Network Volume**: 挂载你创建的 Network Volume 到 `/runpod-volume`
6. **Environment Variables**:
   - `HANDLER_FILE=handler_nsfw.py` (默认已设置)

## 📡 API 使用

### 请求格式

```json
{
  "input": {
    "image_path": "https://example.com/image.jpg",
    "prompt": "A woman dancing gracefully",
    "negative_prompt": "静态，模糊，低质量",
    "seed": 12345,
    "width": 480,
    "height": 640,
    "length": 81,
    "fps": 16,
    "steps": 4,
    "cfg": 1.0,
    "lora_high": "DR34ML4Y_I2V_14B_HIGH.safetensors",
    "lora_low": "DR34ML4Y_I2V_14B_LOW.safetensors",
    "lora_high_strength": 1.0,
    "lora_low_strength": 1.0
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|--------|------|
| `image_path` | string | ✅ | - | 输入图像 (URL/Base64/路径) |
| `prompt` | string | ❌ | "A person walking naturally" | 正向提示词 |
| `negative_prompt` | string | ❌ | "静态，模糊..." | 负向提示词 |
| `seed` | integer | ❌ | 12345 | 随机种子 |
| `width` | integer | ❌ | 480 | 视频宽度 |
| `height` | integer | ❌ | 640 | 视频高度 |
| `length` | integer | ❌ | 81 | 视频帧数 |
| `fps` | integer | ❌ | 16 | 视频帧率 |
| `steps` | integer | ❌ | 4 | 采样步数 |
| `cfg` | float | ❌ | 1.0 | CFG强度 |
| `lora_high` | string | ❌ | "DR34ML4Y_I2V_14B_HIGH.safetensors" | High LoRA 文件名 |
| `lora_low` | string | ❌ | "DR34ML4Y_I2V_14B_LOW.safetensors" | Low LoRA 文件名 |
| `lora_high_strength` | float | ❌ | 1.0 | High LoRA 强度 |
| `lora_low_strength` | float | ❌ | 1.0 | Low LoRA 强度 |

### 响应格式

**成功**:
```json
{
  "video": "base64_encoded_video_data..."
}
```

**失败**:
```json
{
  "error": "Error message"
}
```

## 🔧 使用额外的 LoRA

### 方法1: 上传到 Network Volume (推荐)

```bash
# 上传LoRA文件到:
/runpod-volume/loras/your_custom_lora.safetensors
```

### 方法2: 在 API 请求中指定

```json
{
  "input": {
    "lora_high": "your_custom_lora_high.safetensors",
    "lora_low": "your_custom_lora_low.safetensors"
  }
}
```

## 📝 文件结构

```
wan22_Runpod_hub/
├── Dockerfile                 # 主构建文件
├── handler_nsfw.py           # 核心 API handler (使用你的工作流)
├── handler.py                # 原始 handler (备用)
├── workflow_nsfw.json        # 你的核心工作流
├── entrypoint.sh             # 启动脚本
├── extra_model_paths.yaml    # 模型路径配置
└── DEPLOYMENT_GUIDE.md       # 本文档
```

## ⚙️ 高级配置

### 切换回原始 Handler

如果需要使用原始的 handler.py:

在 RunPod Endpoint 设置中添加环境变量:
```
HANDLER_FILE=handler.py
```

### 模型路径优先级

ComfyUI 会按以下顺序查找模型:
1. `/ComfyUI/models/diffusion_models/NSFW/` (镜像内置)
2. `/runpod-volume/models/NSFW/` (Network Volume) ⭐ 推荐
3. `/ComfyUI/models/diffusion_models/` (镜像内置)
4. `/runpod-volume/models/` (Network Volume)

## 🐛 故障排查

### 问题: "Cannot find NSFW models"

**解决方案**:
1. 确认 Network Volume 已正确挂载到 `/runpod-volume`
2. 检查模型文件是否上传到正确路径
3. 文件名必须完全匹配 (区分大小写)

### 问题: "LoRA not found"

**解决方案**:
1. 检查 `/runpod-volume/loras/` 目录
2. 确认文件名在 API 请求中正确指定

### 问题: "WebSocket connection timeout"

**解决方案**:
1. 增加 GPU 配置
2. 检查 ComfyUI 日志
3. 确认所有模型文件都已正确加载

## 📊 性能建议

- **推荐 GPU**: RTX 4090 (24GB VRAM) 或更高
- **最小 Container Disk**: 180GB
- **Network Volume**: 100GB+ (存储多个模型和 LoRA)
- **预计生成时间**: 2-5 分钟 (取决于视频长度和GPU)

## 🔒 安全提示

- NSFW 内容生成需要遵守当地法律法规
- 建议在 RunPod Endpoint 设置中启用身份验证
- 不要在公共环境暴露 API Key

## 📞 支持

如有问题，请检查:
1. RunPod 容器日志
2. ComfyUI 控制台输出
3. Network Volume 挂载状态

---

**版本**: v1.0
**最后更新**: 2025-12-31
