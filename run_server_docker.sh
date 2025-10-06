set -e  # 遇到错误时退出

echo "🐳 voice-ai-chat-agent-backend Docker本地调试脚本"
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker Desktop"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 设置变量
IMAGE_NAME="voice-ai-chat-agent-backend"
CONTAINER_NAME="voice-ai-chat-agent-backend-debug"
LOCAL_PORT=8000
CONTAINER_PORT=8080
export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897 all_proxy=socks5://127.0.0.1:7897

# 获取Docker Compose项目名称（目录名）
COMPOSE_PROJECT_NAME=$(basename $(pwd))
NETWORK_NAME="${COMPOSE_PROJECT_NAME}_default"

# 清理可能存在的网络冲突
echo "🧹 清理可能存在的网络冲突..."
docker network rm "$NETWORK_NAME" 2>/dev/null || true
docker network rm "$(echo "$NETWORK_NAME" | tr '[:upper:]' '[:lower:]')" 2>/dev/null || true

# 确保使用小写的网络名称（Docker Compose默认行为）
NETWORK_NAME=$(echo "$NETWORK_NAME" | tr '[:upper:]' '[:lower:]')

# 检查网络是否存在，如果不存在则创建
if ! docker network ls | grep -q "$NETWORK_NAME"; then
    echo "🔧 创建Docker网络: $NETWORK_NAME"
    docker network create "$NETWORK_NAME" 2>/dev/null || true
fi

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env文件不存在，将使用示例配置"
    echo "📝 请复制 env_example.txt 为 .env 并配置必要的环境变量"
    if [ -f "env_example.txt" ]; then
        cp env_example.txt .env
        echo "✅ 已创建.env文件，请编辑配置"
    fi
fi

# 停止并删除现有容器和网络
echo "🧹 清理现有容器和网络..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 停止并清理Docker Compose服务
echo "🧹 停止Docker Compose服务..."
docker-compose down --remove-orphans 2>/dev/null || true

# 再次清理网络（确保完全清理）
echo "🧹 最终清理网络..."
docker network rm "$NETWORK_NAME" 2>/dev/null || true
docker network rm "$(echo "$NETWORK_NAME" | tr '[:upper:]' '[:lower:]')" 2>/dev/null || true

# 删除现有镜像（可选，强制重新构建）
if [ "$1" = "--rebuild" ]; then
    echo "🔨 强制重新构建镜像..."
    docker rmi $IMAGE_NAME 2>/dev/null || true
fi

# 启动PostgreSQL数据库
echo "🐘 启动PostgreSQL数据库..."
docker-compose up -d postgres

# 等待网络创建完成
echo "⏳ 等待Docker网络准备就绪..."
sleep 2

# 等待PostgreSQL启动
echo "⏳ 等待PostgreSQL启动..."
sleep 5

# 检查PostgreSQL是否正常运行
if docker-compose ps postgres | grep -q "Up"; then
    echo "✅ PostgreSQL启动成功！"
else
    echo "❌ PostgreSQL启动失败，请检查日志:"
    docker-compose logs postgres
    exit 1
fi

# 创建数据库（如果不存在）
echo "🗄️  检查并创建数据库..."
DB_NAME="voice_ai_chat"
DB_EXISTS=$(docker exec voice_ai_chat_postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
    echo "📝 创建数据库: $DB_NAME"
    docker exec voice_ai_chat_postgres psql -U postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || {
        echo "⚠️  数据库创建失败，但继续运行..."
    }
else
    echo "✅ 数据库 $DB_NAME 已存在"
fi

# 创建数据库表（如果不存在）
echo "📋 检查并创建数据库表..."
docker exec voice_ai_chat_postgres psql -U postgres -d $DB_NAME -c "
-- 创建用户表
CREATE TABLE IF NOT EXISTS \"user\" (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR,
    email VARCHAR,
    avatar_url VARCHAR,
    age INTEGER,
    region VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    preferences TEXT
);

-- 创建健康数据表
CREATE TABLE IF NOT EXISTS healthdata (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES \"user\"(id),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    steps INTEGER DEFAULT 0,
    heart_rate INTEGER DEFAULT 0,
    sleep_hours DECIMAL DEFAULT 0.0,
    calories INTEGER DEFAULT 0,
    distance DECIMAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建AI会话表
CREATE TABLE IF NOT EXISTS aisession (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    language VARCHAR,
    voice_style VARCHAR,
    context_summary TEXT,
    conversation_count INTEGER DEFAULT 0,
    total_duration INTEGER DEFAULT 0,
    session_metadata TEXT
);

-- 创建对话消息表
CREATE TABLE IF NOT EXISTS conversationmessage (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    message_type VARCHAR NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    intent_id INTEGER,
    confidence DECIMAL,
    emotion VARCHAR,
    language VARCHAR DEFAULT 'zh',
    processing_time DECIMAL,
    message_metadata TEXT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_username ON \"user\"(username);
CREATE INDEX IF NOT EXISTS idx_healthdata_user_id ON healthdata(user_id);
CREATE INDEX IF NOT EXISTS idx_aisession_session_id ON aisession(session_id);
CREATE INDEX IF NOT EXISTS idx_aisession_user_id ON aisession(user_id);
CREATE INDEX IF NOT EXISTS idx_conversationmessage_session_id ON conversationmessage(session_id);
CREATE INDEX IF NOT EXISTS idx_conversationmessage_message_type ON conversationmessage(message_type);

-- 创建AI交互日志表（用于log_service）
CREATE TABLE IF NOT EXISTS ai_interactions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR,
    user_id VARCHAR,
    text TEXT,
    reply TEXT,
    emotion VARCHAR,
    intent_id INTEGER,
    confidence DECIMAL,
    explain TEXT,
    language VARCHAR DEFAULT 'zh',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_interactions_session_id ON ai_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_user_id ON ai_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_created_at ON ai_interactions(created_at);
" 2>/dev/null || {
    echo "⚠️  数据库表创建失败，但继续运行..."
}

echo "✅ 数据库表结构检查完成"

# 构建Docker镜像
echo "🔨 构建Docker镜像..."
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "✅ Docker镜像构建成功！"
else
    echo "❌ Docker镜像构建失败！"
    exit 1
fi

# 运行容器
echo "🚀 启动Docker容器..."
echo "🌐 使用网络: $NETWORK_NAME"
docker run -d \
    --name $CONTAINER_NAME \
    --network $NETWORK_NAME \
    -p $LOCAL_PORT:$CONTAINER_PORT \
    -e PORT=$CONTAINER_PORT \
    -e DATABASE_URL=postgresql://postgres:password@postgres:5432/voice_ai_chat \
    -e K_SERVICE=local-debug \
    --env-file .env \
    --restart unless-stopped \
    $IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "✅ Docker容器启动成功！"
    echo ""
    echo "📊 服务信息:"
    echo "  🌐 应用地址: http://localhost:$LOCAL_PORT"
    echo "  📚 API文档: http://localhost:$LOCAL_PORT/docs"
    echo "  🔍 健康检查: http://localhost:$LOCAL_PORT/health"
    echo "  🐘 数据库: localhost:5432"
    echo "  📊 pgAdmin: http://localhost:5050 (admin@voiceaichat.com / admin)"
    echo ""
    echo "📋 常用命令:"
    echo "  查看日志: docker logs -f $CONTAINER_NAME"
    echo "  进入容器: docker exec -it $CONTAINER_NAME bash"
    echo "  停止服务: docker stop $CONTAINER_NAME"
    echo "  重启服务: docker restart $CONTAINER_NAME"
    echo "  删除容器: docker rm -f $CONTAINER_NAME"
    echo ""
    echo "🔍 实时日志 (按 Ctrl+C 退出):"
    docker logs -f $CONTAINER_NAME
else
    echo "❌ Docker容器启动失败！"
    echo "📋 查看错误日志:"
    docker logs $CONTAINER_NAME
    exit 1
fi
