# 🐳 GitHub 自动构建 Docker 镜像配置

## 📋 工作流程

```
你修改代码并 Push 到 GitHub
    ↓
GitHub Actions 自动运行
    ↓
构建 Docker 镜像
    ↓
推送到 GitHub Container Registry (ghcr.io)
    ↓
你在 RunPod 手动选择使用这个镜像
```

**✅ 自动构建镜像**
**✅ 使用 GitHub Container Registry（不需要 Docker Hub 账户）**
**❌ 不自动通知 RunPod**（你手动部署）

---

## 🎯 优势：不需要额外配置！

### **使用 GitHub Container Registry 的好处：**

1. ✅ **不需要 Docker Hub 账户**
2. ✅ **不需要配置任何 Secret**（GitHub 自动提供）
3. ✅ **GitHub Actions 自动登录**
4. ✅ **与 GitHub 仓库集成**
5. ✅ **免费且无限制**

---

## 🚀 使用步骤（零配置）

### 1️⃣ **推送代码触发构建**

```bash
git add .
git commit -m "feat: add auto build workflow"
git push origin main
```

**就这么简单！** GitHub Actions 会自动：
- 构建镜像
- 登录 GitHub Container Registry
- 推送镜像

### 2️⃣ **设置镜像为公开（重要）**

构建完成后，需要将镜像设为公开，RunPod 才能拉取：

1. 进入你的 GitHub 仓库
2. 右侧找到 **Packages** 部分
3. 点击你的镜像包名称
4. **Package settings** → **Change visibility**
5. 选择 **Public**
6. 确认更改

---

## 📦 镜像地址格式

### **完整镜像名称：**
```
ghcr.io/<你的GitHub用户名>/<仓库名>:latest
```

### **例如，如果：**
- 你的 GitHub 用户名是 `yourname`
- 仓库名是 `wan22-runpod`

**镜像地址就是：**
```
ghcr.io/yourname/wan22-runpod:latest
```

---

## 🎯 工作流触发条件

### **自动触发（当修改以下文件时）：**
- `Dockerfile`
- `handler_nsfw.py`
- `handler.py`
- `workflow_nsfw.json`
- `entrypoint.sh`
- `extra_model_paths.yaml`
- `.github/workflows/build-docker.yml`

### **手动触发：**
1. 进入 GitHub 仓库
2. **Actions** 标签
3. 选择 "Build and Push Docker Image"
4. 点击 **Run workflow**
5. 选择分支并点击 **Run workflow**

---

## 📊 查看构建状态

### **在 GitHub：**
1. 进入仓库的 **Actions** 标签
2. 查看 "Build and Push Docker Image" 工作流
3. 查看构建日志和结果

### **构建成功后：**
- 镜像会自动推送到 GitHub Container Registry
- 在仓库右侧可以看到 **Packages**
- 镜像标签：
  - `latest` （最新版本）
  - `main-[commit-sha]` （带提交hash）

---

## 🚀 在 RunPod 中使用镜像

### **步骤：**

1. **在 RunPod Console 创建 Serverless Endpoint**
2. **选择 "Import from a Docker Image"**
3. **填写镜像名称：**
   ```
   ghcr.io/yourname/wan22-runpod:latest
   ```
   ⚠️ **替换 `yourname` 和 `wan22-runpod` 为你的实际用户名和仓库名**

4. **继续配置其他设置**（GPU、Network Volume 等）

---

## 🔄 日常更新流程

### **每次更新代码：**

```bash
# 1. 修改代码
vim handler_nsfw.py

# 2. 提交并推送
git add .
git commit -m "Update handler logic"
git push origin main

# 3. GitHub Actions 自动构建（5-10分钟）
# 在 GitHub Actions 页面查看进度

# 4. 构建完成后，在 RunPod 手动更新镜像
# 进入 Endpoint → 更新 Docker Image → 重启
```

---

## ⏱️ 构建时间预估

| 阶段 | 预计时间 |
|-----|---------|
| 清理磁盘空间 | 30-60 秒 |
| Checkout 代码 | 10-20 秒 |
| 设置 Docker Buildx | 10-20 秒 |
| 登录 GitHub Registry | 5 秒 |
| 构建镜像 | 5-8 分钟 |
| 推送镜像 | 1-2 分钟 |
| **总计** | **7-11 分钟** |

---

## 🐛 故障排查

### Q1: "No space left on device" (磁盘空间不足)
**原因**：GitHub Actions runner 磁盘空间不足（默认约14GB）
**解决**：已通过以下优化解决：
- ✅ 添加构建前磁盘清理步骤（删除 .NET, Android SDK 等）
- ✅ 使用 `--depth=1` 浅克隆 git 仓库
- ✅ 使用 `--no-cache-dir` 避免 pip 缓存
- ✅ 克隆后立即删除 `.git` 目录
- ✅ 合并多个 RUN 命令减少 Docker 层数

**效果**：可释放约 10-12 GB 磁盘空间

### Q2: "Package not found" 或 "Pull access denied"
**原因**：镜像还未设置为公开
**解决**：
1. 进入 GitHub → 仓库 → Packages
2. 点击镜像
3. Package settings → Change visibility → Public

### Q3: "Workflow not triggered"
**原因**：修改的文件不在触发路径中
**解决**：
- 手动触发（Actions → Run workflow）
- 或修改核心文件（Dockerfile, handler 等）

### Q4: "Build failed"
**原因**：Dockerfile 有错误
**解决**：
1. 查看 GitHub Actions 日志
2. 修复错误
3. 重新 push

---

## 💡 对比：GitHub Container Registry vs Docker Hub

| 特性 | GitHub Container Registry | Docker Hub |
|-----|--------------------------|-----------|
| **需要额外账户** | ❌ 不需要 | ✅ 需要 |
| **需要配置 Secret** | ❌ 不需要 | ✅ 需要 |
| **自动登录** | ✅ 是 | ❌ 否 |
| **费用** | ✅ 免费 | ✅ 免费（有限制）|
| **集成度** | ✅ 原生集成 GitHub | ❌ 需要手动配置 |

**推荐：GitHub Container Registry！** ⭐

---

## ✅ 配置完成检查清单

- [ ] 推送代码到 GitHub
- [ ] GitHub Actions 构建成功
- [ ] 将镜像设置为 Public
- [ ] 镜像已出现在 GitHub Packages
- [ ] 在 RunPod 中测试使用镜像

---

## 🎉 总结

**使用 GitHub Container Registry 的优势：**
- ✅ **零配置** - 不需要任何 Secret
- ✅ **自动登录** - GitHub 自动处理
- ✅ **完全免费** - 无限制使用
- ✅ **原生集成** - 与 GitHub 完美整合

**只需 push 代码，GitHub 自动构建并推送镜像！** 🚀
