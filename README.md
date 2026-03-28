# 垃圾分类系统 (Trash Classification System)

基于 Qwen (通义千问) 大模型的垃圾分类前后端分离项目。支持通过 AI 智能识别垃圾类别，并提供完整的用户注册、登录、意见反馈、分类字典查询及后台管理功能。

---

## 🚀 快速上手 (How to Run)

如果您刚刚克隆了此仓库，希望在本地机器上把这个项目跑起来，请严格按照以下步骤进行配置。

### 0. 准备环境 (Prerequisites)

请确保你的电脑上已经安装了：
- **Python 3.9+** (建议使用 Conda 或 venv 创建虚拟环境)
- **Node.js** (推荐v16+版本，包含 npm)
- **MySQL 8.0+** 数据库服务

---

### 1. 克隆项目 (Clone Repository)

```bash
git clone https://github.com/yeliheng-010/QwenTrashClassification.git
cd QwenTrashClassification
```

---

### 2. 数据库准备 (Database Setup)

请在你的 MySQL 中新建一个空数据库（比如叫 `garbage_classification`），你可以使用 Navicat 或者命令行创建：
```sql
CREATE DATABASE garbage_classification DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### 3. 配置与启动后端 (Backend Setup & Run)

后端是基于 **FastAPI + SQLAlchemy** 构建的。

#### 3.1 配置文件 (`.env`)
进入到 `backend` 目录下：
```bash
cd backend
```
将项目的配置模板复制一份，并重命名为正式的 `.env`。**这个文件必须手动创建！**
```bash
cp .env.example .env
```
用编辑器打开刚创建的 `.env` 文件，完善你的配置信息：
- `DATABASE_URL`: 修改为你的对应 MySQL 用户名、密码和第2步中创建的数据库名称。例如 `mysql+pymysql://root:123456@127.0.0.1:3306/garbage_classification`
- `SILICONFLOW_API_KEY`: 填入你的硅基流动 (SiliconFlow) 大模型 API Key。如果你想要测试垃圾识别功能，这个配置必须填写。
- `SECRET_KEY`: 这是用来加密 JWT Token 的密钥，可以随便填一串复杂的字母+数字组合。

#### 3.2 安装依赖
如果你使用 conda，可以新建或激活虚拟环境后安装依赖（或者根据你的习惯直接安装）：
```bash
pip install -r requirements.txt
```

#### 3.3 启动后端服务器
依赖安装完成后，启动服务：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*💡 **特别提示**：如果在应用启动时数据库为空，后端会自动建表，并默默写入一个默认密码：**`admin123`**，默认账号：**`superadmin`** 的超级管理员账号，供您直接登录后台体验完整功能！*

✅ 当终端打印出 `Application startup complete.`，代表后端在 `http://127.0.0.1:8000` 运行成功了！

---

### 4. 启动前端 (Frontend Setup & Run)

前端基于 **Vue 3 + Vite + Element Plus** 开发，如果需要与后端交互请**另开一个终端窗口**。

#### 4.1 安装依赖包
从项目根目录进入到 `frontend` 文件夹：
```bash
cd frontend
npm install
```

#### 4.2 启动本地开发服务环境
```bash
npm run dev
```

✅ 看到包含 `http://localhost:5173/` 或者 `http://127.0.0.1:5173/` 网址的日志后，就能直接在浏览器里面打开对应的地址体验完整的项目功能啦！🚀

---

## 🐳 Docker 一键部署体验版 (Docker Compose)

如果你熟悉 Docker，不想在本地处理 Python 和 Node.js 环境，可以使用写好的 `docker-compose.yml` 快速部署。
> **前提**: 必须在本地 `backend` 目录下手动创建好完全正常的 `.env` 配置（参照 3.1 的内容），否则后端容器会由于缺少数据库密码信息导致反复重启报错。

1. 修改后端环境配置并保存 `.env`。
2. 在项目根目录（带有 `docker-compose.yml` 的那一级），运行构建：
   ```bash
   docker-compose up -d --build
   ```
3. 构建完成后，您能通过 `http://localhost:8080/` 访问网页前端（前端映射为了 `8080`），通过 `http://localhost:8000/docs` 查看后端接口文档。

---

如果遇到项目重启报错，或者启动后访问报错 500、验证失败，请第一时间检查后端 `.env` 下的 `DATABASE_URL` MySQL 用户名密码配置是否完全符合你本地这台电脑的实际环境。
