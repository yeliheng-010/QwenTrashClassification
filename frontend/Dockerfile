# 第一阶段：构建 (Build Stage)
# 使用 node 18 作为基础镜像进行构建
FROM node:18 AS build-stage

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建项目
RUN npm run build

# 第二阶段：生产环境 (Production Stage)
# 使用 nginx:alpine 作为生产环境镜像
FROM nginx:alpine AS production-stage

# 将构建好的 dist 目录复制到 nginx 的默认静态文件目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 暴露 80 端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
