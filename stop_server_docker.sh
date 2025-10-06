echo "🛑 停止 voice-ai-chat-agent-backend Docker调试环境"
echo "=============================="

# 设置变量
CONTAINER_NAME="voice-ai-chat-agent-backend-debug"

# 停止并删除应用容器
echo "🧹 停止应用容器..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 停止PostgreSQL和pgAdmin
echo "🐘 停止数据库服务..."
docker-compose down

echo "✅ 所有服务已停止！"
echo ""
echo "📋 清理命令:"
echo "  删除所有容器: docker rm -f \$(docker ps -aq)"
echo "  删除所有镜像: docker rmi \$(docker images -q)"
echo "  删除所有卷: docker volume prune -f"
echo "  完全清理: docker system prune -a -f"
