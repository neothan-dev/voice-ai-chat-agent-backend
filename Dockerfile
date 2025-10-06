# 使用Python 3.11官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --fix-missing \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据库目录
RUN mkdir -p dbfiles

# 创建日志目录
RUN mkdir -p logs

# 给run_server.sh添加执行权限
RUN chmod +x ./run_server.sh

# 暴露端口（Cloud Run会通过环境变量PORT指定）
EXPOSE 8080

# 启动命令 - 使用run_server.sh脚本
CMD ["./run_server.sh"]