#!/usr/bin/env python3
"""
测试 Replicate 模型并显示详细日志
"""
import replicate
import os

# 设置 API Token
# export REPLICATE_API_TOKEN=your_token
# 或者直接设置: os.environ["REPLICATE_API_TOKEN"] = "r8_..."

def test_model():
    print("🚀 开始测试模型...")
    print("=" * 60)

    # 创建预测
    model_version = "hzeyuan/wan-model"

    prediction = replicate.predictions.create(
        version=model_version,
        input={
            "prompt": "你好,请介绍一下自己",
            "max_new_tokens": 256,
            "temperature": 0.7,
        }
    )

    print(f"📋 预测 ID: {prediction.id}")
    print(f"🔗 查看详情: https://replicate.com/p/{prediction.id}")
    print("=" * 60)

    # 实时获取日志
    print("\n📝 实时日志:")
    print("-" * 60)

    # 使用 stream 获取实时输出
    for event in replicate.stream(
        model_version,
        input={
            "prompt": "你好,请介绍一下自己",
            "max_new_tokens": 256,
            "temperature": 0.7,
        }
    ):
        print(event, end="")

    print("\n" + "-" * 60)

    # 获取完整预测信息
    prediction.reload()

    print(f"\n✅ 状态: {prediction.status}")
    print(f"⏱️  开始时间: {prediction.created_at}")
    print(f"⏱️  完成时间: {prediction.completed_at}")

    if prediction.metrics:
        print(f"\n📊 性能指标:")
        print(f"  - 预测时间: {prediction.metrics.get('predict_time', 'N/A')}s")

    if prediction.logs:
        print(f"\n📋 完整日志:")
        print("-" * 60)
        print(prediction.logs)
        print("-" * 60)

    if prediction.output:
        print(f"\n💬 输出结果:")
        print("=" * 60)
        print(prediction.output)
        print("=" * 60)

    if prediction.error:
        print(f"\n❌ 错误: {prediction.error}")

def test_with_lora():
    """测试 LoRA 加载"""
    print("\n🔧 测试 LoRA 功能...")
    print("=" * 60)

    output = replicate.run(
        "hzeyuan/wan-model",
        input={
            "prompt": "写一首关于春天的诗",
            "lora_path": "",  # 这里填入你的 LoRA repo
            "lora_scale": 0.8,
            "max_new_tokens": 512,
        }
    )

    print("输出:", output)

if __name__ == "__main__":
    # 检查 API token
    if not os.getenv("REPLICATE_API_TOKEN"):
        print("❌ 请设置 REPLICATE_API_TOKEN 环境变量")
        print("export REPLICATE_API_TOKEN=your_token")
        exit(1)

    test_model()

    # 取消注释以测试 LoRA
    # test_with_lora()
