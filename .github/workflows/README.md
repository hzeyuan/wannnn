# GitHub Actions 自动部署

## 设置步骤

### 1. 获取 Replicate API Token

1. 访问 https://replicate.com/auth/token
2. 复制你的 API token

### 2. 添加 GitHub Secret

1. 在 GitHub 仓库页面,进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下 secret:
   - Name: `REPLICATE_API_TOKEN`
   - Value: 粘贴你的 Replicate token

### 3. 触发部署

**自动触发:**
```bash
git add .
git commit -m "Update model"
git push origin main
```

**手动触发:**
1. 进入 GitHub 仓库的 **Actions** 标签
2. 选择 "Deploy to Replicate" workflow
3. 点击 **Run workflow**

## 工作流程

```
git push → GitHub Actions 开始
         ↓
      安装 Cog
         ↓
      登录 Replicate
         ↓
    构建 Docker 镜像
         ↓
    推送到 Replicate
         ↓
       部署完成
```

## 预计时间

- 安装 Cog: ~30秒
- 构建镜像: ~5-10分钟
- 推送镜像: ~2-3分钟
- **总计: ~10-15分钟**

## 查看日志

在 GitHub Actions 页面可以实时查看构建日志和进度。

## 本地开发

如果需要本地测试:
```bash
cog predict -i prompt="测试"
```

本地测试不影响已部署的版本。
