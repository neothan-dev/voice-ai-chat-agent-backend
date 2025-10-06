echo "🚀 开始部署 voice-ai-chat-agent-backend 到Google Cloud Run..."

export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897 all_proxy=socks5://127.0.0.1:7897

# 检查是否在backend目录
if [ ! -f "main.py" ]; then
    echo "❌ 错误: 请在backend目录下运行此脚本"
    exit 1
fi

# 检查.env文件是否存在（可选）
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到.env文件"
    echo "Cloud Run将使用Cloud Build设置的环境变量"
else
    echo "✅ 找到.env配置文件"
    echo "📝 注意: Cloud Run中.env配置文件的某些变量(数据库路径等)将被Cloud Build环境变量覆盖"
fi

# 检查gcloud是否安装
if ! command -v gcloud &> /dev/null; then
    echo "❌ 错误: gcloud CLI未安装，请先安装Google Cloud SDK"
    echo "安装指南: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# 检查是否已登录
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 请先登录Google Cloud..."
    gcloud auth login
fi

# 设置项目ID
PROJECT_ID=""
echo "📋 设置项目ID: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# 启用必要的API
echo "🔧 启用必要的API..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# 构建并部署
echo "🏗️  开始构建和部署..."
gcloud builds submit --config cloudbuild.yaml --substitutions=COMMIT_SHA=local .

if [ $? -eq 0 ]; then
    echo "✅ 部署成功！"
    echo "🌐 获取服务URL..."
    SERVICE_URL=$(gcloud run services describe voice-ai-chat-agent-backend --region=asia-east1 --format="value(status.url)")
    echo "🎉 服务已部署到: $SERVICE_URL"
    echo "📊 查看日志: gcloud logs tail --service=voice-ai-chat-agent-backend --region=asia-east1"
    
    # 询问是否要测试服务
    echo ""
    read -p "🧪 是否要测试服务？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🧪 开始测试服务..."
        source venv/bin/activate
        python3 scripts/test_deployment.py "$SERVICE_URL"
    fi
else
    echo "❌ 部署失败，请检查日志"
    exit 1
fi
