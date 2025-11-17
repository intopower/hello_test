# TV Commentary Studio

自动化地将长篇电视剧素材转换为短视频解说稿与成片示例的实验性应用。系统包含：

- **FastAPI 后端**：负责任务创建、状态管理以及多阶段媒体管线调度，并将任务/素材持久化到 `storage/`。
- **React + Vite 前端**：提供精美、可视化的操作界面，可上传素材、配置解说偏好并实时查看进度、时间线与脚本。
- **多媒体服务层**：封装真实的 OpenAI Whisper/LLM/TTS（自动回退占位实现），方便替换为其他云服务或私有模型。

> ⚠️ 请在根目录复制 `.env.example` 为 `.env` 并填写 `OPENAI_API_KEY`，即可启用真实 ASR/脚本/TTS 能力；未配置时自动回退为占位逻辑。

## 快速开始

### 0. 环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY 等信息
```

### 1. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

默认服务监听 `http://localhost:8000`，媒体与任务数据默认写入仓库根目录下的 `storage/`。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

Vite 默认在 `http://localhost:5173`，并通过 `VITE_API_BASE` 环境变量（可在 `.env` 中配置）访问后端。

## 功能概览

- 导入视频文件并填写语言、音色、目标时长等解说参数。
- 后端以任务状态机串联“解析 → 脚本 → 剪辑 → 配音”，输出制作时间线、脚本段落、AI 配音与 BGM 建议。
- 自动调用 OpenAI Whisper（语音转写）、GPT-4o-mini（脚本）、GPT-4o-mini-tts（配音），没有 API Key 时会优雅退回占位实现。
- 所有任务、脚本、媒体文件持久化存储，可刷新后继续查看与下载。
- 前端面板提供进度条、彩色时间线、视频预览、脚本列表以及配音音频播放器。
- 结构化代码，便于后续对接真实模型与任务队列（Celery/Kafka 等）。

## 项目结构

```
backend/
  app/
    api/          # FastAPI 路由
    core/         # 配置管理
    schemas/      # Pydantic 数据模型
    services/     # 存储、转写、脚本、剪辑、TTS、任务管理
    workflows/    # 管线编排
frontend/
  src/
    api.ts        # 与后端交互
    types.ts      # 前端类型定义
    App.tsx       # 主界面
storage/
  media/          # 上传与生成的媒体资源
  data/tasks.json # 任务持久化
```

## Docker 一键部署

```bash
docker compose build
docker compose up
```

- 后端：`http://localhost:8000`，会读取根目录 `.env`，并把媒体/数据保存在宿主的 `storage/` 目录。
- 前端：`http://localhost:4173`，默认通过 `http://backend:8000/api` 访问后端。

## 下一步规划

- 将 `app/services/` 下的 OpenAI 实现替换为企业私有大模型或多云策略。
- 使用 Celery/Kafka 等消息队列取代 FastAPI BackgroundTask，提升并发与容错。
- 在前端加入可拖拽时间轴、内容审核提示、团队协作等高级特性。
