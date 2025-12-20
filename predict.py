from cog import BasePredictor, Input, Path as CogPath
import torch
from diffusers import WanPipeline
from PIL import Image
import os

# 使用官方 Wan-AI Diffusers 模型
MODEL_CACHE = "model_cache"
# 可选模型:
# - Wan-AI/Wan2.2-T2V-A14B-Diffusers (文本生成视频)
# - Wan-AI/Wan2.2-I2V-A14B-Diffusers (图片生成视频)
# - Wan-AI/Wan2.2-TI2V-5B-Diffusers (文本+图片生成视频, 5B更小)
MODEL_ID = "Wan-AI/Wan2.2-T2V-A14B-Diffusers"

class Predictor(BasePredictor):
    def setup(self):
        """加载 Wan 2.2 视频生成模型"""
        print(f"Loading Wan 2.2 model: {MODEL_ID}")

        # 设置缓存目录
        os.makedirs(MODEL_CACHE, exist_ok=True)

        # 加载 pipeline
        self.pipeline = WanPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.bfloat16,
            cache_dir=MODEL_CACHE,
        )

        # 移到 GPU
        self.pipeline.to("cuda")

        # 启用内存优化
        self.pipeline.enable_model_cpu_offload()
        self.pipeline.enable_vae_slicing()

        print("Model loaded successfully!")

    def predict(
        self,
        prompt: str = Input(
            description="描述你想生成的视频内容",
            default="A beautiful sunset over the ocean with waves crashing"
        ),
        image: CogPath = Input(
            description="输入图片 (可选, 用于图片生成视频模式)",
            default=None
        ),
        num_frames: int = Input(
            description="生成的视频帧数",
            default=49,
            ge=17,
            le=121
        ),
        num_inference_steps: int = Input(
            description="推理步数 (越多质量越好但越慢)",
            default=30,
            ge=10,
            le=100
        ),
        guidance_scale: float = Input(
            description="引导系数 (越高越符合提示词)",
            default=7.0,
            ge=1.0,
            le=20.0
        ),
        height: int = Input(
            description="视频高度",
            default=720,
            choices=[480, 720]
        ),
        width: int = Input(
            description="视频宽度",
            default=1280,
            choices=[832, 1280]
        ),
        fps: int = Input(
            description="视频帧率",
            default=24,
            ge=8,
            le=30
        ),
        seed: int = Input(
            description="随机种子 (留空随机生成)",
            default=None
        ),
    ) -> CogPath:
        """生成视频"""

        # 设置随机种子
        if seed is None:
            seed = torch.randint(0, 2**32 - 1, (1,)).item()

        generator = torch.Generator(device="cuda").manual_seed(seed)

        print(f"Generating video...")
        print(f"  Prompt: {prompt}")
        print(f"  Resolution: {width}x{height}")
        print(f"  Frames: {num_frames} @ {fps}fps")
        print(f"  Steps: {num_inference_steps}")
        print(f"  Seed: {seed}")

        # 准备输入参数
        pipeline_kwargs = {
            "prompt": prompt,
            "num_frames": num_frames,
            "height": height,
            "width": width,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "generator": generator,
        }

        # 如果提供了图片,加载它
        if image is not None:
            print(f"  Using input image: {image}")
            input_image = Image.open(str(image)).convert("RGB")
            pipeline_kwargs["image"] = input_image

        # 生成视频
        output = self.pipeline(**pipeline_kwargs)

        # 获取视频帧
        video_frames = output.frames[0]  # [num_frames, height, width, 3]

        # 保存为视频文件
        output_path = "/tmp/output.mp4"

        # 使用 imageio 保存视频
        import imageio
        imageio.mimwrite(
            output_path,
            video_frames,
            fps=fps,
            codec='libx264',
            quality=8
        )

        print(f"Video saved to: {output_path}")

        return CogPath(output_path)
