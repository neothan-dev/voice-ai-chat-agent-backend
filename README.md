# voice-ai-chat-agent-backend

<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/README.md"><img alt="README in English" src="https://img.shields.io/badge/English-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-CN.md"><img alt="简体中文操作指南" src="https://img.shields.io/badge/简体中文-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-JP.md"><img alt="日本語のREADME" src="https://img.shields.io/badge/日本語-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-KR.md"><img alt="README in 한국어" src="https://img.shields.io/badge/한국어-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-ES.md"><img alt="README en Español" src="https://img.shields.io/badge/Español-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-FR.md"><img alt="README en Français" src="https://img.shields.io/badge/Français-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-IT.md"><img alt="README in Italiano" src="https://img.shields.io/badge/Italiano-lightgrey"></a>

A FastAPI-based AI voice chat backend service supporting real-time voice interaction, user management, data configuration, and cloud deployment.

## ✨ Features

- 🎤 **Real-time voice interaction**: Supports Speech-to-Text (STT) and Text-to-Speech (TTS)
- 🤖 **AI chat**: Integrates OpenAI GPT models to provide intelligent conversation
- 👤 **User management**: Complete user registration, login, and session management
- 📊 **Data configuration**: Flexible configuration of application data via Excel files
- 🌐 **WebSocket support**: Real-time bidirectional communication
- 🚀 **One-click deployment**: Supports one-click deployment to Google Cloud Run
- 🔧 **Extensible architecture**: Modular design, easy to extend

## 🏗️ Architecture

```
├── api/                    # API route modules
│   ├── auth.py          # User authentication
│   ├── ai.py            # AI conversation endpoints
│   ├── speech.py        # Speech processing
│   ├── navigation.py    # Navigation features
│   ├── dashboard.py     # Dashboard
│   ├── device.py       # Device management
│   └── health.py       # Health check
├── core/                 # Core modules
│   ├── config.py       # Configuration management
│   └── db.py           # Database connection
├── models/              # Data models
│   ├── user.py         # User model
│   ├── session.py      # Session model
│   └── health_data.py  # Health data model
├── services/            # Business services
│   ├── ai_comprehensive_service.py  # AI comprehensive service
│   ├── stt_service.py  # Speech to text
│   ├── tts_service.py  # Text to speech
│   ├── emotion_service.py  # Sentiment analysis
│   ├── translation_service.py  # Translation service
│   └── ...
├── utils/               # Utility modules
│   ├── config_manager.py  # Configuration loader
│   └── excel_to_code.py   # Excel to code
├── dev/data/           # Development data
│   ├── excel/          # Excel configuration files
│   └── code/           # Generated config code
└── main.py             # Application entrypoint
```

## 🚀 Quick Start

### Requirements

- Python 3.8+
- PostgreSQL 12+
- Various AI service API keys

### Installation Steps

1. **Clone the project**
```bash
git clone https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
cd voice-ai-chat-agent-backend
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp env_example.txt .env
```

Edit the `.env` file to configure required API keys:

```env
# Database configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/voice_ai_db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Azure Cognitive Services
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_EMOTION_KEY=your_azure_emotion_key_here
AZURE_EMOTION_ENDPOINT=your_azure_emotion_endpoint_here

# Google Cloud API
GOOGLE_APPLICATION_CREDENTIALS=credential/your_google_cloud_credential.json

# Other settings...
```

5. **Initialize the database**
```bash
# Ensure PostgreSQL service is running
# Create the database
createdb voice_ai_db

# Run the app (will auto-initialize the database)
python main.py
```

6. **Start the service**
```bash
# Development mode
python main.py

# Or use uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` to view the API documentation.

## 📋 Configuration

### Environment variables

| Name | Description | Required |
|--------|-------------|----------|
| `DATABASE_URL` | Database connection URL | ✅ |
| `OPENAI_API_KEY` | OpenAI API key | ✅ |
| `AZURE_SPEECH_KEY` | Azure Speech Service key | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud credentials file path | ✅ |
| `SECRET_KEY` | JWT authentication secret | ✅ |
| `HOST` | Server host | ❌ |
| `PORT` | Server port | ❌ |
| `DEBUG` | Debug mode | ❌ |

### Excel configuration system

The project supports configuring application data via Excel files for flexible data management:

1. **Create Excel files**: Create `.xlsx` files in `dev/data/excel/`
2. **Configure data**: Fill data following the template format
3. **Automatic conversion**: System automatically converts Excel to Python configuration code
4. **Dynamic loading**: Supports hot reload; updates configuration after Excel changes

#### Using the configuration loader

```python
from utils.config_manager import CONFIG_LOADER

# Get a config
config = CONFIG_LOADER.get_config('navigation')

# Get config of a specific sheet
sheet_config = CONFIG_LOADER.get_config_sheet('navigation', 'routes')

# Get a specific config value
value = CONFIG_LOADER.get_config_value('navigation', 'routes', 'home_path')
```

## 🔧 API Endpoints

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token
- `GET /auth/me` - Get current user info

### AI Conversation

- `POST /ai/chat` - Send chat message
- `WebSocket /ai/chat/ws` - Real-time chat connection
- `GET /ai/history` - Get chat history

### Speech

- `POST /speech/stt` - Speech to text
- `POST /speech/tts` - Text to speech
- `WebSocket /speech/ws` - Real-time speech stream

### Navigation

- `GET /navigation/routes` - Get navigation routes
- `POST /navigation/update` - Update navigation configuration

## 🐳 Docker Deployment

### Run locally with Docker

```bash
# Build image
docker build -t voice-ai-chat-agent-backend .

# Run container
docker run -p 8000:8000 --env-file .env voice-ai-chat-agent-backend
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## ☁️ Google Cloud Deployment

### One-click deployment

```bash
# Configure Google Cloud CLI
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Run deployment script
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### Manual deployment

1. **Build image**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy voice-ai-chat-agent-backend \
  --image gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run a specific test
pytest tests/test_auth.py

# Generate coverage report
pytest --cov=api --cov-report=html
```

## 📊 Monitoring and Logging

### Logging configuration

Log file location: `logs/app.log`

Log level can be configured via the `LOG_LEVEL` environment variable.

## 🔒 Security Considerations

- JWT token authentication
- Password hashing and storage
- CORS configuration
- Protect sensitive info with environment variables
- API rate limiting (configurable)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Development Guide

### Add a new API endpoint

1. Create a new route file in `api/`
2. Register the route in `main.py`
3. Add corresponding data models (if needed)
4. Write test cases

### Add a new configuration

1. Create an Excel file under `dev/data/excel/`
2. Fill data following the template format
3. Load configuration using `CONFIG_LOADER`

### Code style

- Use type hints
- Follow PEP 8
- Add appropriate docstrings
- Write unit tests

## 🐛 Troubleshooting

### Common issues

1. **Database connection failed**
   - Check whether PostgreSQL service is running
   - Verify the database connection URL
   - Confirm database user permissions

2. **API key errors**
   - Check environment variable configuration
   - Verify API key validity
   - Confirm service quotas

3. **Excel configuration not applied**
   - Check Excel file format
   - Confirm correct file path
   - View conversion logs

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [OpenAI](https://openai.com/) - AI model services
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/) - Speech and sentiment analysis
- [Google Cloud](https://cloud.google.com/) - Cloud services support

## 📞 Support

If you have questions or suggestions:

1. Check [Issues](https://github.com/neothan-dev/voice-ai-chat-agent-backend/issues)
2. Create a new Issue
3. Contact the maintainers

---

⭐ If this project helps you, please give it a star!
