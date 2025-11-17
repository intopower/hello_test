# TV Commentary Studio

自动化地将长篇电视剧素材转换为短视频解说稿与成片示例的实验性应用。系统包含：

- **FastAPI 后端**：负责任务创建、状态管理以及（当前为模拟的）多阶段处理管线。
- **React + Vite 前端**：提供精美、可视化的操作界面，可上传素材、配置解说偏好并实时查看任务进度与脚本。

> ⚠️ 当前管线仍为占位逻辑，主要用于演示整体架构，可在 `backend/app/workflows/pipeline.py` 中替换为真实的 ASR、LLM、剪辑与 TTS 能力。

## 快速开始

### 1. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

默认服务监听 `http://localhost:8000`。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

Vite 默认在 `http://localhost:5173`，并通过 `VITE_API_BASE` 环境变量（可在 `.env` 中配置）访问后端。

## 功能概览

- 导入视频文件并填写语言、音色、目标时长等解说参数。
- 后端以任务状态机模拟“分析→脚本→剪辑→渲染”流程。
- 前端任务面板展示实时进度、状态 Tag 以及自动生成的脚本段落。
- 结构化代码，便于后续对接真实模型和任务队列（Celery/Kafka 等）。

## 项目结构

```
backend/
  app/
    api/          # FastAPI 路由
    core/         # 配置管理
    schemas/      # Pydantic 数据模型
    services/     # 任务服务抽象
    workflows/    # 处理管线（占位逻辑）
frontend/
  src/
    api.ts        # 与后端交互
    types.ts      # 前端类型定义
    App.tsx       # 主界面
```

## 下一步规划

- 接入真实的语音转写、LLM 脚本生成、自动剪辑与 TTS 能力。
- 引入对象存储/数据库与消息队列，保证任务可追溯与扩展。
- 在前端加入时间轴拖拽、预览播放器、内容审核提示等高级可视化能力。
