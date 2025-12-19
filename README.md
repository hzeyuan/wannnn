# WAN2.2-14B-Rapid-AllInOne Replicate 部署指南

这是将 WAN2.2-14B-Rapid-AllInOne 模型部署到 Replicate 的完整配置,支持动态 LoRA 加载。

## 功能特性

- ✅ 基于 Qwen2.5 的 14B 参数模型
- ✅ 支持动态加载 HuggingFace LoRA
- ✅ 支持本地 LoRA 文件
- ✅ LoRA 权重缩放控制
- ✅ 完整的生成参数控制
- ✅ 自动 GPU 分配和优化

## 部署步骤

### 1. 安装 Cog

**macOS/Linux:**
```bash
sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
sudo chmod +x /usr/local/bin/cog
```

**验证安装:**
```bash
cog --version
```

### 2. 本地测试

**测试基础模型:**
```bash
cog predict -i prompt="你好,请介绍一下自己"
```

**测试带 LoRA:**
```bash
cog predict -i prompt="写一首诗" -i lora_path="username/your-lora-repo"
```

**完整参数测试:**
```bash
cog predict \
  -i prompt="请写一个关于未来的故事" \
  -i lora_path="username/your-lora" \
  -i lora_scale=0.8 \
  -i max_new_tokens=1024 \
  -i temperature=0.9 \
  -i top_p=0.95
```

### 3. 推送到 Replicate

**登录 Replicate:**
```bash
cog login
```

**推送模型:**
```bash
cog push r8.im/your-username/wan-model
```

## API 使用

推送成功后,可以通过 API 调用:

**Python:**
```python
import replicate

output = replicate.run(
    "your-username/wan-model",
    input={
        "prompt": "你好,请介绍一下自己",
        "lora_path": "username/lora-repo",  # 可选
        "lora_scale": 1.0,
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9
    }
)
print(output)
```

**cURL:**
```bash
curl -s -X POST \
  -H "Authorization: Token $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "YOUR_MODEL_VERSION",
    "input": {
      "prompt": "你好",
      "lora_path": "username/lora-repo"
    }
  }' \
  https://api.replicate.com/v1/predictions
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | string | - | 输入提示文本 (必需) |
| `lora_path` | string | "" | LoRA路径,留空使用基础模型 |
| `lora_scale` | float | 1.0 | LoRA权重强度 (0.0-2.0) |
| `max_new_tokens` | int | 512 | 最大生成token数 (1-2048) |
| `temperature` | float | 0.7 | 温度参数,越高越随机 (0.1-2.0) |
| `top_p` | float | 0.9 | Nucleus采样阈值 (0.0-1.0) |
| `top_k` | int | 50 | Top-k采样,0表示禁用 (0-100) |
| `repetition_penalty` | float | 1.1 | 重复惩罚 (1.0-2.0) |

## LoRA 使用指南

### 使用 HuggingFace LoRA

```bash
cog predict \
  -i prompt="你的提示" \
  -i lora_path="username/lora-repo"
```

### LoRA 权重调整

```bash
# 降低 LoRA 影响
cog predict -i prompt="..." -i lora_path="..." -i lora_scale=0.5

# 增强 LoRA 影响
cog predict -i prompt="..." -i lora_path="..." -i lora_scale=1.5
```

### 切换 LoRA

模型会自动处理 LoRA 切换:
- 首次指定 LoRA 时会加载
- 更换 LoRA 路径时会自动切换
- lora_path 留空时会卸载回基础模型

## 性能优化建议

### 显存优化

如果遇到 OOM,可以修改 [predict.py](predict.py:18-24):

```python
# 启用 4-bit 量化
self.base_model = AutoModelForCausalLM.from_pretrained(
    model_path,
    subfolder="Mega-v12",
    load_in_4bit=True,
    device_map="auto",
    trust_remote_code=True
)
```

### 预装常用 LoRA

如果有固定的几个常用 LoRA,可以预装以提速:

```python
def setup(self):
    # ... 基础模型加载 ...

    # 预装 LoRA
    self.preloaded_loras = {
        "style1": PeftModel.from_pretrained(self.base_model, "path/to/lora1"),
        "style2": PeftModel.from_pretrained(self.base_model, "path/to/lora2"),
    }
```

## 成本估算

- **GPU 需求:** 至少 24GB 显存 (A100/A10G)
- **首次构建:** 约 20-30 分钟 (下载模型)
- **后续启动:** 约 2-5 分钟 (加载到 GPU)
- **推理成本:** 约 $0.0023/秒 (A100)

## 故障排查

### Cog 构建失败

```bash
# 查看详细日志
cog build --debug
```

### 模型下载超时

在 [predict.py](predict.py:8-14) 中添加重试:

```python
from huggingface_hub import snapshot_download

# 预下载模型
snapshot_download(
    "Phr00t/WAN2.2-14B-Rapid-AllInOne",
    local_dir="/src/model_cache"
)
```

### LoRA 加载失败

检查 LoRA 是否与基础模型兼容:
- 必须是 PEFT 格式
- 必须基于相同或兼容的基础模型训练

## 进阶配置

### 添加系统提示词

```python
def predict(self, prompt: str, system_prompt: str = Input(default="你是一个有帮助的助手"), ...):
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
    # ... 其余代码
```

### 支持流式输出

Replicate 目前不直接支持流式输出,但可以分块返回:

```python
from cog import BasePredictor, Input, ConcatenateIterator

def predict(self, ...) -> ConcatenateIterator[str]:
    # 返回迭代器实现伪流式
    for token in self.model.generate(...):
        yield self.tokenizer.decode(token)
```

## 相关资源

- [Replicate 文档](https://replicate.com/docs)
- [Cog 文档](https://github.com/replicate/cog)
- [PEFT 文档](https://huggingface.co/docs/peft)
- [模型主页](https://huggingface.co/Phr00t/WAN2.2-14B-Rapid-AllInOne)

## License

遵循原模型许可协议。
