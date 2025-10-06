# voice-ai-chat-agent-backend

<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/README.md"><img alt="README in English" src="https://img.shields.io/badge/English-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-CN.md"><img alt="简体中文操作指南" src="https://img.shields.io/badge/简体中文-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-JP.md"><img alt="日本語のREADME" src="https://img.shields.io/badge/日本語-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-KR.md"><img alt="README in 한국어" src="https://img.shields.io/badge/한국어-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-ES.md"><img alt="README en Español" src="https://img.shields.io/badge/Español-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-FR.md"><img alt="README en Français" src="https://img.shields.io/badge/Français-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-IT.md"><img alt="README in Italiano" src="https://img.shields.io/badge/Italiano-lightgrey"></a>

一个基于FastAPI的AI语音聊天后端服务，支持实时语音交互、用户管理、数据配置和云端部署。

## ✨ 特性

- 🎤 **实时语音交互**: 支持语音转文字(STT)和文字转语音(TTS)
- 🤖 **AI对话**: 集成OpenAI GPT模型，提供智能对话
- 👤 **用户管理**: 完整的用户注册、登录和会话管理
- 📊 **数据配置**: 通过Excel文件灵活配置应用数据
- 🌐 **WebSocket支持**: 实时双向通信
- 🚀 **一键部署**: 支持Google Cloud Run一键部署
- 🔧 **可扩展架构**: 模块化设计，易于扩展

## 🏗️ 架构

```
├── api/                    # API路由模块
│   ├── auth.py          # 用户认证
│   ├── ai.py            # AI对话接口
│   ├── speech.py        # 语音处理
│   ├── navigation.py    # 导航功能
│   ├── dashboard.py     # 仪表板
│   ├── device.py       # 设备管理
│   └── health.py       # 健康检查
├── core/                 # 核心模块
│   ├── config.py       # 配置管理
│   └── db.py           # 数据库连接
├── models/              # 数据模型
│   ├── user.py         # 用户模型
│   ├── session.py      # 会话模型
│   └── health_data.py  # 健康数据模型
├── services/            # 业务服务
│   ├── ai_comprehensive_service.py  # AI综合服务
│   ├── stt_service.py  # 语音转文字
│   ├── tts_service.py  # 文字转语音
│   ├── emotion_service.py  # 情感分析
│   ├── translation_service.py  # 翻译服务
│   └── ...
├── utils/               # 工具模块
│   ├── config_manager.py  # 配置管理器
│   └── excel_to_code.py   # Excel转代码
├── dev/data/           # 开发数据
│   ├── excel/          # Excel配置文件
│   └── code/           # 生成的配置代码
└── main.py             # 应用入口
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- PostgreSQL 12+
- 各种AI服务API密钥

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
cd voice-ai-chat-agent-backend
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp env_example.txt .env
```

编辑 `.env` 文件，配置必要的API密钥：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/voice_ai_db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Azure 认知服务
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_EMOTION_KEY=your_azure_emotion_key_here
AZURE_EMOTION_ENDPOINT=your_azure_emotion_endpoint_here

# Google Cloud API
GOOGLE_APPLICATION_CREDENTIALS=credential/your_google_cloud_credential.json

# 其他配置...
```

5. **初始化数据库**
```bash
# 确保PostgreSQL服务运行
# 创建数据库
createdb voice_ai_db

# 运行应用（会自动初始化数据库）
python main.py
```

6. **启动服务**
```bash
# 开发模式
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs` 查看API文档。

## 📋 配置说明

### 环境变量配置

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DATABASE_URL` | 数据库连接URL | ✅ |
| `OPENAI_API_KEY` | OpenAI API密钥 | ✅ |
| `AZURE_SPEECH_KEY` | Azure语音服务密钥 | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud凭证文件路径 | ✅ |
| `SECRET_KEY` | JWT认证密钥 | ✅ |
| `HOST` | 服务器主机 | ❌ |
| `PORT` | 服务器端口 | ❌ |
| `DEBUG` | 调试模式 | ❌ |

### Excel配置系统

项目支持通过Excel文件配置应用数据，实现灵活的数据管理：

1. **创建Excel文件**: 在 `dev/data/excel/` 目录下创建 `.xlsx` 文件
2. **配置数据**: 按照模板格式填写数据
3. **自动转换**: 系统会自动将Excel转换为Python配置代码
4. **动态加载**: 支持热重载，修改Excel后自动更新配置

#### 使用配置管理器

```python
from utils.config_manager import CONFIG_LOADER

# 获取配置
config = CONFIG_LOADER.get_config('navigation')

# 获取特定sheet的配置
sheet_config = CONFIG_LOADER.get_config_sheet('navigation', 'routes')

# 获取特定配置值
value = CONFIG_LOADER.get_config_value('navigation', 'routes', 'home_path')
```

## 🔧 API接口

### 认证接口

- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新令牌
- `GET /auth/me` - 获取当前用户信息

### AI对话接口

- `POST /ai/chat` - 发送聊天消息
- `WebSocket /ai/chat/ws` - 实时聊天连接
- `GET /ai/history` - 获取聊天历史

### 语音接口

- `POST /speech/stt` - 语音转文字
- `POST /speech/tts` - 文字转语音
- `WebSocket /speech/ws` - 实时语音流

### 导航接口

- `GET /navigation/routes` - 获取导航路由
- `POST /navigation/update` - 更新导航配置

## 🐳 Docker部署

### 本地Docker运行

```bash
# 构建镜像
docker build -t voice-ai-chat-agent-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env voice-ai-chat-agent-backend
```

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## ☁️ Google Cloud部署

### 一键部署

```bash
# 配置Google Cloud CLI
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 运行部署脚本
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### 手动部署

1. **构建镜像**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend
```

2. **部署到Cloud Run**
```bash
gcloud run deploy voice-ai-chat-agent-backend \
  --image gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 测试

```bash
# 运行测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=api --cov-report=html
```

## 📊 监控和日志

### 日志配置

日志文件位置：`logs/app.log`

日志级别可通过环境变量 `LOG_LEVEL` 配置。

## 🔒 安全考虑

- JWT令牌认证
- 密码加密存储
- CORS配置
- 环境变量保护敏感信息
- API速率限制（可配置）

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 开发指南

### 添加新的API接口

1. 在 `api/` 目录下创建新的路由文件
2. 在 `main.py` 中注册路由
3. 添加相应的数据模型（如需要）
4. 编写测试用例

### 添加新的配置

1. 在 `dev/data/excel/` 目录下创建Excel文件
2. 按照模板格式配置数据
3. 使用 `CONFIG_LOADER` 加载配置

### 代码规范

- 使用类型提示
- 遵循PEP 8规范
- 添加适当的文档字符串
- 编写单元测试

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查PostgreSQL服务是否运行
   - 验证数据库连接URL
   - 确认数据库用户权限

2. **API密钥错误**
   - 检查环境变量配置
   - 验证API密钥有效性
   - 确认服务配额

3. **Excel配置不生效**
   - 检查Excel文件格式
   - 确认文件路径正确
   - 查看转换日志

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Web框架
- [OpenAI](https://openai.com/) - AI模型服务
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/) - 语音和情感分析
- [Google Cloud](https://cloud.google.com/) - 云服务支持

## 📞 支持

如有问题或建议，请：

1. 查看 [Issues](https://github.com/neothan-dev/voice-ai-chat-agent-backend/issues)
2. 创建新的Issue
3. 联系维护者

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
