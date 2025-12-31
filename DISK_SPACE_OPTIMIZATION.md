# 🔧 GitHub Actions 磁盘空间优化说明

## 问题背景

GitHub Actions 的免费 runner 磁盘空间约 14GB，但构建包含多个 ComfyUI 自定义节点的 Docker 镜像需要更多空间。

## 已实施的优化措施

### 📦 Dockerfile 优化

1. **使用 `--no-cache-dir`**
   - 所有 `pip install` 命令添加此参数
   - 避免 pip 缓存占用磁盘空间
   - 节省约 500MB - 1GB

2. **浅克隆 git 仓库 (`--depth=1`)**
   - 只克隆最新提交，不下载完整历史
   - 大幅减小每个仓库的体积（通常减少 70-90%）
   - 节省约 1-2GB

3. **立即删除 .git 目录**
   - 克隆后立即执行 `rm -rf .git`
   - 构建容器不需要 git 历史
   - 节省约 500MB - 1GB

4. **合并 RUN 命令**
   - 将多个 RUN 合并为单个层
   - 减少 Docker 中间层数量
   - 节省约 500MB

5. **清理 Python 缓存**
   ```dockerfile
   find /ComfyUI/custom_nodes -type f -name "*.pyc" -delete
   find /ComfyUI/custom_nodes -type d -name "__pycache__" -delete
   ```
   - 删除编译后的 Python 字节码
   - 节省约 100-200MB

### ⚙️ GitHub Actions 优化

1. **删除预装软件**
   - 删除 .NET SDK (~1.2GB)
   - 删除 Android SDK (~8GB)
   - 删除 Haskell (~2GB)
   - 删除 CodeQL (~1GB)
   - 删除 Boost (~500MB)
   - **总计释放：~12-13GB**

2. **清理 Docker 缓存**
   ```bash
   sudo docker system prune -af --volumes
   ```
   - 清理悬空镜像和容器
   - 释放约 1-2GB

3. **禁用 provenance 和 SBOM**
   ```yaml
   provenance: false
   sbom: false
   ```
   - 减少构建元数据
   - 节省约 100-200MB

## 总体效果

| 优化类别 | 节省空间 |
|---------|---------|
| GitHub Runner 清理 | ~12-13GB |
| Dockerfile 优化 | ~3-5GB |
| Docker 构建优化 | ~1-2GB |
| **总计可用空间增加** | **~16-20GB** |

## 如果仍然失败的备选方案

### 方案 A：本地构建并推送

如果 GitHub Actions 仍然空间不足，可以在本地构建：

```bash
# 1. 本地构建镜像
docker build -t ghcr.io/<你的用户名>/wan22_runpod_hub:latest .

# 2. 登录 GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u <你的用户名> --password-stdin

# 3. 推送镜像
docker push ghcr.io/<你的用户名>/wan22_runpod_hub:latest
```

**优点**：
- ✅ 不受 GitHub runner 限制
- ✅ 可以使用本地磁盘空间
- ✅ 构建速度可能更快（取决于网络）

**缺点**：
- ❌ 需要手动执行
- ❌ 需要本地 Docker 环境

### 方案 B：使用更小的基础镜像

当前基础镜像：`wlsdml1114/multitalk-base:1.4`

可以考虑切换到官方 NVIDIA CUDA 镜像：
```dockerfile
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04
```

**优点**：
- ✅ 官方镜像，更小更优化
- ✅ 更好的维护和安全更新

**缺点**：
- ❌ 需要重新安装所有依赖
- ❌ 可能缺少某些预装工具

### 方案 C：使用 GitHub 付费 runner

GitHub 提供更大磁盘空间的 runner（需要付费）：
- `ubuntu-latest-4-cores`: ~14GB 磁盘
- `ubuntu-latest-8-cores`: ~14GB 磁盘
- `ubuntu-latest-16-cores`: ~14GB 磁盘

注意：付费 runner 磁盘空间与免费版相同，但 CPU 和内存更多。

### 方案 D：分阶段构建

将构建分为多个 workflow，每个处理一部分：

1. **Stage 1**: 构建基础层（ComfyUI + 基础依赖）
2. **Stage 2**: 添加自定义节点
3. **Stage 3**: 最终配置

**优点**：
- ✅ 每个阶段占用空间更小
- ✅ 可以利用层缓存

**缺点**：
- ❌ 配置更复杂
- ❌ 总构建时间可能更长

## 监控构建过程

查看磁盘使用情况：

1. 进入 GitHub → Actions → 选择失败的 workflow
2. 查看 "Maximize disk space" 步骤
3. 检查 "Before cleanup" 和 "After cleanup" 的输出
4. 确认清理是否生效

## 下一步

1. ✅ 推送优化后的代码
2. ⏳ 等待 GitHub Actions 构建
3. 📊 查看构建日志，确认磁盘清理生效
4. 🎉 如果成功，将镜像设为 Public
5. ❌ 如果仍失败，考虑使用备选方案 A（本地构建）

---

**最后更新**: 2025-12-31
**状态**: 已优化，等待测试
