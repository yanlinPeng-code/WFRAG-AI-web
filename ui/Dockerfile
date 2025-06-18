# 使用官方 Node.js 镜像作为基础镜像
FROM node:20 as builder

# 设置工作目录
WORKDIR /app/web

# 将 package.json 和 yarn.lock 拷贝到镜像内
COPY package.json .
COPY yarn.lock .

# 使用 yarn 安装依赖
RUN yarn install

# 将项目代码拷贝到容器中
COPY . .

# 配置环境变量
ENV VITE_API_PREFIX=/api

# 构建/编译项目
RUN yarn build

# 二阶段使用 Nginx 来部署 Vue 静态页面
FROM nginx:alpine as production
COPY --from=builder /app/web/dist /usr/share/nginx/html
COPY --from=builder /app/web/docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# 设置目录权限为 755，确保 Nginx 可以访问目录
RUN find /usr/share/nginx/html -type d -exec chmod 755 {} \;

# 设置文件权限为 644，确保文件可以读但不可执行
RUN find /usr/share/nginx/html -type f -exec chmod 644 {} \;

# 暴露 3000 端口号
EXPOSE 3000

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]