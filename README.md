# 🍃 基于 Qwen 大模型的智能垃圾分类系统

![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=flat&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?style=flat&logo=docker)
![Qwen LLM](https://img.shields.io/badge/AI_Model-Qwen_Turbo-blueviolet?style=flat)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📖 项目简介

本项目是一个基于 **B/S 架构** 与 **大语言模型（LLM）** 深度结合的智能环保服务平台。系统旨在解决传统垃圾分类查询中存在的“口语化描述识别率低、复合型垃圾难以拆解”等痛点。

通过接入**阿里云通义千问（Qwen）大模型**，本系统赋予了原本冷冰冰的知识库以强大的语义理解与逻辑推理能力。用户只需用日常自然语言提问（如：“没喝完的珍珠奶茶连着塑料杯怎么扔？”），系统即可智能拆解成分并给出精准的投放建议。

系统采用现代化全栈技术开发，UI 视觉风格采用温暖治愈的浅色系，并全面支持 **Docker 容器化一键部署**，真正实现“一次构建，到处运行”。

## ✨ 核心特性

### 🧑‍💻 用户端 (Client)
- **🤖 AI 智能问答**：基于 Qwen 大模型，支持长文本、口语化、复杂语境的垃圾分类智能推理。
- **📚 兜底检索与图鉴**：内置本地高频垃圾分类词库与四大分类（干/湿/可回收/有害）标准图鉴，断网或 API 异常时无缝降级。
- **📰 环保资讯社区**：浏览最新环保政策、科普文章。
- **📊 历史追溯与反馈**：自动记录问答历史，支持针对 AI 幻觉的纠错反馈闭环。
- **🎨 社交分享**：支持一键生成专属环保科普图文海报并保存到相册/分享。

### 🛡️ 管理员端 (Admin)
- **📈 可视化监控仪表盘**：全景监控注册用户量、API 调用频次、热门搜索垃圾词云。
- **👥 用户全生命周期管理**：账号重置、状态封禁与解封。
- **📝 动态知识库维护**：后台增删改查本地标准词库与环保科普资讯。
- **🔄 AI 语料闭环与系统日志**：审核用户纠错反馈，积累调优提示词（Prompt）语料；实时查看底层运行日志保障系统高可用。

## 🛠️ 技术栈选型

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **前端 (Frontend)** | Vue 3 + Vite + Pinia + Vue Router + Axios | 采用组合式 API，单页面应用 (SPA)，温暖治愈系浅色 UI |
| **后端 (Backend)** | Python 3.10+ + FastAPI + Pydantic | 基于 ASGI 标准的高性能异步并发框架 |
| **数据库 (Database)** | MySQL 8.0 + SQLAlchemy (ORM) | 持久化存储，采用连接池与预编译防注入 |
| **AI 引擎 (AI Model)** | Aliyun DashScope SDK (Qwen) | 通义千问大语言模型 API |
| **部署 (Deployment)** | Docker + Docker Compose | 容器化隔离运行环境，极致简化部署流程 |

## 🚀 快速启动 (Quick Start)

### 1. 环境准备
请确保你的宿主机已安装 [Docker](https://www.docker.com/) 和 [Docker Compose](https://docs.docker.com/compose/)。

### 2. 克隆项目
```bash
git clone [https://github.com/你的用户名/你的仓库名.git](https://github.com/你的用户名/你的仓库名.git)
cd 你的项目目录
### 3  配置环境变量

4. 一键容器化部署
执行以下命令，Docker 将自动拉取依赖、构建镜像并启动前后端及数据库容器：

Bash
docker-compose up -d --build
5. 访问服务
用户前台页面: http://localhost:80

后台接口文档 (Swagger UI): http://localhost:8000/docs
