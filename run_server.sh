#!/bin/bash
echo "🚀 启动Voice AI Chat后端应用..."

# 环境检测函数
detect_environment() {
    if [ -n "$K_SERVICE" ]; then
        echo "🌐 检测到Cloud Run环境: $K_SERVICE"
        ENVIRONMENT="cloud_run"
    elif [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
        echo "🐳 检测到Docker容器环境"
        ENVIRONMENT="docker"
    else
        echo "💻 检测到本地开发环境"
        ENVIRONMENT="local"
    fi
}

# 数据库连接配置函数
setup_database() {
    case $ENVIRONMENT in
        "cloud_run")
            echo "🌐 Cloud Run环境：使用Cloud SQL数据库连接"
            # Cloud Run环境通常通过环境变量配置数据库连接
            # 数据库连接字符串应该通过环境变量DATABASE_URL提供
            if [ -n "$DATABASE_URL" ]; then
                echo "✅ 使用环境变量DATABASE_URL配置数据库连接"
            else
                echo "⚠️  警告: 未设置DATABASE_URL环境变量"
            fi
            ;;
        "docker")
            echo "🐳 使用Docker网络数据库连接"
            # Docker容器环境连接到PostgreSQL容器
            export DATABASE_URL="postgresql://postgres:password@postgres:5432/voice_ai_chat"
            echo "✅ 数据库连接已配置: postgres:5432"
            ;;
        "local")
            echo "💻 启动本地PostgreSQL数据库..."
            
            # 检查Docker是否安装
            if ! command -v docker &> /dev/null; then
                echo "错误: Docker未安装，请先安装Docker"
                exit 1
            fi

            # 检查Docker Compose是否安装
            if ! command -v docker-compose &> /dev/null; then
                echo "错误: Docker Compose未安装，请先安装Docker Compose"
                exit 1
            fi

            # 检查Docker是否运行
            if ! docker info > /dev/null 2>&1; then
                echo "❌ Docker未运行，请先启动Docker Desktop"
                exit 1
            fi

            # 启动PostgreSQL服务
            echo "启动PostgreSQL容器..."
            docker-compose up -d postgres

            # 等待PostgreSQL启动
            echo "等待PostgreSQL启动..."
            sleep 5

            # 检查PostgreSQL是否正常运行
            if docker-compose ps postgres | grep -q "Up"; then
                echo "PostgreSQL启动成功！"
                echo "数据库连接信息:"
                echo "  Host: localhost"
                echo "  Port: 5432"
                echo "  Database: voice_ai_chat"
                echo "  Username: postgres"
                echo "  Password: password"
                echo ""
                # 设置本地数据库连接
                export DATABASE_URL="postgresql://postgres:password@localhost:5432/voice_ai_chat"
            else
                echo "PostgreSQL启动失败，请检查日志:"
                docker-compose logs postgres
                exit 1
            fi
            ;;
    esac
}

# 虚拟环境设置函数
setup_virtual_environment() {
    if [ "$ENVIRONMENT" = "local" ] && [ -d "venv" ]; then
        echo "🔧 激活虚拟环境..."
        source venv/bin/activate
    fi
}

# 代理设置函数
setup_proxy() {
    # 仅在本地环境设置代理
    if [ "$ENVIRONMENT" = "local" ]; then
        echo "🌐 设置代理..."
        export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897 all_proxy=socks5://127.0.0.1:7897
    fi
}

# 依赖安装函数
install_dependencies() {
    echo "📦 安装Python依赖..."
    pip install -r ./requirements.txt
}

# 启动服务器函数
start_server() {
    echo "🚀 启动FastAPI服务器..."
    
    case $ENVIRONMENT in
        "cloud_run")
            # Cloud Run环境：使用环境变量PORT，不启用reload
            echo "🌐 Cloud Run模式：端口 ${PORT:-8080}"
            exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
            ;;
        "docker")
            # Docker容器环境：使用环境变量PORT，不启用reload
            echo "🐳 Docker容器模式：端口 ${PORT:-8080}"
            exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
            ;;
        "local")
            # 本地开发环境：启用reload
            echo "💻 本地开发模式：启用热重载"
            exec uvicorn main:app --reload \
              --reload-dir ./api \
              --reload-dir ./services \
              --reload-dir ./core \
              --reload-dir ./utils \
              --host 0.0.0.0 \
              --port 8000
            ;;
    esac
}

# 主执行流程
main() {
    # 1. 检测运行环境
    detect_environment
    
    # 2. 设置数据库连接
    setup_database
    
    # 3. 设置虚拟环境
    setup_virtual_environment
    
    # 4. 设置代理
    setup_proxy
    
    # 5. 安装依赖
    install_dependencies
    
    # 6. 启动服务器
    start_server
}

# 执行主函数
main
