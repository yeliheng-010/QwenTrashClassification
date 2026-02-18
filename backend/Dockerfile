# 使用 python 3.10-slim 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 安装依赖
# --no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下的所有文件到工作目录
COPY . .

# 暴露 8000 端口
EXPOSE 8000

# 启动命令
# 使用 uvicorn 启动应用，监听 0.0.0.0:8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
