# 🐳 GitHub 自动构建 Docker 镜像配置

## 📋 工作流程

```
你修改代码并 Push 到 GitHub
    ↓
GitHub Actions 自动运行
    ↓
构建 Docker 镜像
    ↓
推送到 Docker Hub
    ↓
你在 RunPod 手动选择使用这个镜像
```

**✅ 自动构建镜像**
**❌ 不自动通知 RunPod**（你手动部署）

---

## 🔧 初次配置步骤

### 1️⃣ 创建 Docker Hub Access Token

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 点击右上角头像 → **Account Settings**
3. 左侧菜单 → **Security** → **Personal Access Tokens**
4. 点击 **New Access Token**
5. 输入 Token 名称（如 `github-actions`）
6. 权限选择：**Read, Write, Delete**
7. 点击 **Generate**
8. **复制生成的 Token**（只显示一次，保存好！）

### 2️⃣ 在 GitHub 仓库设置 Secrets

1. 进入你的 GitHub 仓库
2. **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下两个 Secret：

#### Secret 1: DOCKERHUB_USERNAME
- **Name**: `DOCKERHUB_USERNAME`
- **Value**: 你的 Docker Hub 用户名（如 `yourname`）

#### Secret 2: DOCKERHUB_TOKEN
- **Name**: `DOCKERHUB_TOKEN`
- **Value**: 刚才复制的 Access Token

### 3️⃣ 推送代码触发构建

```bash
git add .
git commit -m "feat: add auto build workflow"
git push origin main
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
- 镜像会自动推送到 Docker Hub
- 镜像标签：
  - `yourname/wan22-nsfw:latest` （最新版本）
  - `yourname/wan22-nsfw:main-[commit-sha]` （带提交hash）

---

## 🚀 在 RunPod 中使用构建的镜像

### **方法 1：创建新 Endpoint 时**
1. 在 RunPod Console 创建 Serverless Endpoint
2. 选择 **"Import from a Docker Image"**
3. 填写镜像名称：
   ```
   yourname/wan22-nsfw:latest
   ```
4. 继续配置其他设置

### **方法 2：更新现有 Endpoint**
1. 进入现有 Endpoint 设置
2. 更新 Docker Image
3. 填写新的镜像名称
4. 保存并重启

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
| Checkout 代码 | 10-20 秒 |
| 设置 Docker Buildx | 10-20 秒 |
| 登录 Docker Hub | 5 秒 |
| 构建镜像 | 5-8 分钟 |
| 推送到 Docker Hub | 1-2 分钟 |
| **总计** | **6-10 分钟** |

---

## 💡 优化建议

### **使用构建缓存：**
工作流已配置缓存，第二次构建会更快：
- 首次构建：~8 分钟
- 后续构建：~3-5 分钟

### **并行构建多个标签：**
当前配置会生成：
- `latest` - 最新版本
- `main-[sha]` - 带提交 hash 的版本

---

## 🐛 故障排查

### Q1: "Login failed"
**原因**：Docker Hub Token 不正确
**解决**：
1. 检查 GitHub Secrets 中的 `DOCKERHUB_TOKEN`
2. 重新生成 Docker Hub Access Token
3. 更新 Secret

### Q2: "Build failed: permission denied"
**原因**：Token 权限不足
**解决**：确保 Token 有 **Read, Write, Delete** 权限

### Q3: "Push failed: repository not found"
**原因**：Docker Hub 用户名错误
**解决**：检查 `DOCKERHUB_USERNAME` 是否正确

### Q4: "Workflow not triggered"
**原因**：修改的文件不在触发路径中
**解决**：手动触发或修改 `.github/workflows/build-docker.yml`

---

## 📦 镜像信息

### **镜像名称格式：**
```
<你的Docker Hub用户名>/wan22-nsfw:latest
```

### **例如：**
```
yourname/wan22-nsfw:latest
```

### **在 RunPod 中使用：**
```bash
# 完整镜像名称
yourname/wan22-nsfw:latest

# 或者使用特定版本
yourname/wan22-nsfw:main-abc1234
```

---

## ✅ 配置完成检查清单

- [ ] Docker Hub Access Token 已创建
- [ ] GitHub Secrets 已配置（DOCKERHUB_USERNAME, DOCKERHUB_TOKEN）
- [ ] 推送代码到 GitHub
- [ ] GitHub Actions 构建成功
- [ ] 镜像已出现在 Docker Hub
- [ ] 在 RunPod 中测试使用镜像

---

## 🎉 优势总结

✅ **自动构建** - Push 代码自动触发
✅ **版本控制** - 每次构建都有唯一标签
✅ **缓存优化** - 后续构建更快
✅ **手动部署** - 在 RunPod 中你决定何时更新
✅ **镜像轻量** - 不包含模型文件（~5GB）

**配置完成后，你只需要 push 代码，GitHub 自动构建并推送镜像到 Docker Hub！** 🚀
