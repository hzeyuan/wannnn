from cog import BasePredictor, Input
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

MODEL_NAME = "Phr00t/WAN2.2-14B-Rapid-AllInOne"
MODEL_SUBFOLDER = "Mega-v12"

class Predictor(BasePredictor):
    def setup(self):
        """加载基础模型到内存"""
        print(f"Loading model: {MODEL_NAME}/{MODEL_SUBFOLDER}")
        print("Note: First run will download ~28GB model, cached for future runs")

        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            subfolder=MODEL_SUBFOLDER,
            trust_remote_code=True
        )

        print("Loading base model...")
        self.base_model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            subfolder=MODEL_SUBFOLDER,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
            # HuggingFace 会自动缓存到 ~/.cache/huggingface
            # Replicate 会持久化这个目录
        )

        # 追踪当前加载的LoRA
        self.current_lora = None
        self.model = self.base_model
        print("Model loaded successfully!")

    def predict(
        self,
        prompt: str = Input(description="输入提示文本"),
        lora_path: str = Input(
            description="LoRA路径 (HuggingFace repo如'username/repo'或本地路径,留空使用基础模型)",
            default=""
        ),
        lora_scale: float = Input(
            description="LoRA权重强度",
            default=1.0,
            ge=0.0,
            le=2.0
        ),
        max_new_tokens: int = Input(
            description="最大生成token数",
            default=512,
            ge=1,
            le=2048
        ),
        temperature: float = Input(
            description="温度参数 (越高越随机)",
            default=0.7,
            ge=0.1,
            le=2.0
        ),
        top_p: float = Input(
            description="Top-p采样 (nucleus sampling)",
            default=0.9,
            ge=0.0,
            le=1.0
        ),
        top_k: int = Input(
            description="Top-k采样",
            default=50,
            ge=0,
            le=100
        ),
        repetition_penalty: float = Input(
            description="重复惩罚",
            default=1.1,
            ge=1.0,
            le=2.0
        ),
    ) -> str:
        """运行模型推理"""

        # 处理LoRA加载逻辑
        lora_path = lora_path.strip()

        if lora_path and lora_path != self.current_lora:
            # 需要加载新的LoRA
            print(f"Loading LoRA from: {lora_path}")
            try:
                self.model = PeftModel.from_pretrained(
                    self.base_model,
                    lora_path,
                    torch_dtype=torch.bfloat16,
                )
                self.current_lora = lora_path
                print(f"LoRA loaded successfully")
            except Exception as e:
                print(f"Failed to load LoRA: {e}")
                print("Falling back to base model")
                self.model = self.base_model
                self.current_lora = None

        elif not lora_path and self.current_lora:
            # 卸载当前LoRA,回到基础模型
            print("Unloading LoRA, using base model")
            self.model = self.base_model
            self.current_lora = None

        # 如果使用LoRA,设置缩放比例
        if self.current_lora and hasattr(self.model, 'set_adapter_scale'):
            self.model.set_adapter_scale(lora_scale)

        # 准备输入
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        # 生成参数
        gen_kwargs = {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k if top_k > 0 else None,
            "repetition_penalty": repetition_penalty,
            "do_sample": True,
        }

        # 运行推理
        print(f"Generating with {len(inputs['input_ids'][0])} input tokens...")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **gen_kwargs
            )

        # 解码结果
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return result
