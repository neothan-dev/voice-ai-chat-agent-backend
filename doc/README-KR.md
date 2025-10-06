# voice-ai-chat-agent-backend

<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/README.md"><img alt="README in English" src="https://img.shields.io/badge/English-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-CN.md"><img alt="简体中文操作指南" src="https://img.shields.io/badge/简体中文-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-JP.md"><img alt="日本語のREADME" src="https://img.shields.io/badge/日本語-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-KR.md"><img alt="README in 한국어" src="https://img.shields.io/badge/한국어-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-ES.md"><img alt="README en Español" src="https://img.shields.io/badge/Español-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-FR.md"><img alt="README en Français" src="https://img.shields.io/badge/Français-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-IT.md"><img alt="README in Italiano" src="https://img.shields.io/badge/Italiano-lightgrey"></a>

FastAPI 기반 AI 음성 채팅 백엔드 서비스로, 실시간 음성 상호작용, 사용자 관리, 데이터 구성 및 클라우드 배포를 지원합니다.

## ✨ 특징

- 🎤 **실시간 음성 상호작용**: 음성 인식(STT) 및 음성 합성(TTS) 지원
- 🤖 **AI 대화**: OpenAI GPT 모델을 통합하여 지능형 대화 제공
- 👤 **사용자 관리**: 사용자 등록, 로그인 및 세션 관리 제공
- 📊 **데이터 구성**: Excel 파일을 통한 유연한 애플리케이션 데이터 구성
- 🌐 **WebSocket 지원**: 실시간 양방향 통신
- 🚀 **원클릭 배포**: Google Cloud Run에 원클릭 배포 지원
- 🔧 **확장 가능한 아키텍처**: 모듈형 설계로 확장 용이

## 🏗️ 아키텍처

```
├── api/                    # API 라우트 모듈
│   ├── auth.py          # 사용자 인증
│   ├── ai.py            # AI 대화 엔드포인트
│   ├── speech.py        # 음성 처리
│   ├── navigation.py    # 내비게이션 기능
│   ├── dashboard.py     # 대시보드
│   ├── device.py       # 디바이스 관리
│   └── health.py       # 상태 점검
├── core/                 # 코어 모듈
│   ├── config.py       # 구성 관리
│   └── db.py           # 데이터베이스 연결
├── models/              # 데이터 모델
│   ├── user.py         # 사용자 모델
│   ├── session.py      # 세션 모델
│   └── health_data.py  # 건강 데이터 모델
├── services/            # 비즈니스 서비스
│   ├── ai_comprehensive_service.py  # AI 종합 서비스
│   ├── stt_service.py  # 음성 → 텍스트
│   ├── tts_service.py  # 텍스트 → 음성
│   ├── emotion_service.py  # 감정 분석
│   ├── translation_service.py  # 번역 서비스
│   └── ...
├── utils/               # 유틸리티 모듈
│   ├── config_manager.py  # 구성 로더
│   └── excel_to_code.py   # Excel → 코드
├── dev/data/           # 개발 데이터
│   ├── excel/          # Excel 구성 파일
│   └── code/           # 생성된 구성 코드
└── main.py             # 애플리케이션 진입점
```

## 🚀 빠른 시작

### 환경 요구 사항

- Python 3.8+
- PostgreSQL 12+
- 다양한 AI 서비스 API 키

### 설치 단계

1. **프로젝트 클론**
```bash
git clone https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
cd voice-ai-chat-agent-backend
```

2. **가상 환경 생성**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경 변수 설정**
```bash
cp env_example.txt .env
```

`.env` 파일을 편집하여 필요한 API 키를 구성합니다:

```env
# 데이터베이스 구성
DATABASE_URL=postgresql://postgres:password@localhost:5432/voice_ai_db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Azure Cognitive Services
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_EMOTION_KEY=your_azure_emotion_key_here
AZURE_EMOTION_ENDPOINT=your_azure_emotion_endpoint_here

# Google Cloud API
GOOGLE_APPLICATION_CREDENTIALS=credential/your_google_cloud_credential.json

# 기타 설정...
```

5. **데이터베이스 초기화**
```bash
# PostgreSQL 서비스가 실행 중인지 확인
# 데이터베이스 생성
createdb voice_ai_db

# 애플리케이션 실행 (DB 자동 초기화)
python main.py
```

6. **서비스 시작**
```bash
# 개발 모드
python main.py

# 또는 uvicorn 사용
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`http://localhost:8000/docs` 에 접속하여 API 문서를 확인하세요.

## 📋 구성 설명

### 환경 변수

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `DATABASE_URL` | 데이터베이스 연결 URL | ✅ |
| `OPENAI_API_KEY` | OpenAI API 키 | ✅ |
| `AZURE_SPEECH_KEY` | Azure 음성 서비스 키 | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud 자격 증명 파일 경로 | ✅ |
| `SECRET_KEY` | JWT 인증 비밀키 | ✅ |
| `HOST` | 서버 호스트 | ❌ |
| `PORT` | 서버 포트 | ❌ |
| `DEBUG` | 디버그 모드 | ❌ |

### Excel 구성 시스템

본 프로젝트는 Excel 파일을 통해 애플리케이션 데이터를 구성하여 유연한 데이터 관리를 지원합니다:

1. **Excel 파일 생성**: `dev/data/excel/` 디렉터리에 `.xlsx` 파일 생성
2. **데이터 구성**: 템플릿 형식에 따라 데이터 입력
3. **자동 변환**: 시스템이 Excel을 Python 구성 코드로 자동 변환
4. **동적 로드**: 핫 리로드 지원, Excel 변경 후 구성 자동 업데이트

#### 구성 로더 사용

```python
from utils.config_manager import CONFIG_LOADER

# 구성 가져오기
config = CONFIG_LOADER.get_config('navigation')

# 특정 시트의 구성 가져오기
sheet_config = CONFIG_LOADER.get_config_sheet('navigation', 'routes')

# 특정 구성 값 가져오기
value = CONFIG_LOADER.get_config_value('navigation', 'routes', 'home_path')
```

## 🔧 API 엔드포인트

### 인증

- `POST /auth/register` - 사용자 등록
- `POST /auth/login` - 로그인
- `POST /auth/refresh` - 토큰 갱신
- `GET /auth/me` - 현재 사용자 정보

### AI 대화

- `POST /ai/chat` - 채팅 메시지 전송
- `WebSocket /ai/chat/ws` - 실시간 채팅 연결
- `GET /ai/history` - 채팅 기록 조회

### 음성

- `POST /speech/stt` - 음성 → 텍스트
- `POST /speech/tts` - 텍스트 → 음성
- `WebSocket /speech/ws` - 실시간 음성 스트림

### 내비게이션

- `GET /navigation/routes` - 내비게이션 라우트 조회
- `POST /navigation/update` - 내비게이션 구성 업데이트

## 🐳 Docker 배포

### 로컬에서 Docker 실행

```bash
# 이미지 빌드
docker build -t voice-ai-chat-agent-backend .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env voice-ai-chat-agent-backend
```

### Docker Compose

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## ☁️ Google Cloud 배포

### 원클릭 배포

```bash
# Google Cloud CLI 설정
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 배포 스크립트 실행
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### 수동 배포

1. **이미지 빌드**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend
```

2. **Cloud Run에 배포**
```bash
gcloud run deploy voice-ai-chat-agent-backend \
  --image gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 테스트

```bash
# 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_auth.py

# 커버리지 리포트 생성
pytest --cov=api --cov-report=html
```

## 📊 모니터링 및 로그

### 로그 구성

로그 파일 위치: `logs/app.log`

로그 레벨은 환경 변수 `LOG_LEVEL`로 설정할 수 있습니다.

## 🔒 보안 고려 사항

- JWT 토큰 인증
- 비밀번호 해시화 및 저장
- CORS 구성
- 환경 변수로 민감 정보 보호
- API 속도 제한(설정 가능)

## 🤝 기여 가이드

1. 저장소 Fork
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경 사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📝 개발 가이드

### 새로운 API 엔드포인트 추가

1. `api/`에 새로운 라우트 파일 생성
2. `main.py`에 라우트 등록
3. 필요한 경우 데이터 모델 추가
4. 테스트 케이스 작성

### 새로운 구성 추가

1. `dev/data/excel/`에 Excel 파일 생성
2. 템플릿 형식에 따라 데이터 구성
3. `CONFIG_LOADER`로 구성 로드

### 코드 스타일

- 타입 힌트 사용
- PEP 8 준수
- 적절한 도큐멘트 문자열 추가
- 단위 테스트 작성

## 🐛 문제 해결

### 일반적인 문제

1. **데이터베이스 연결 실패**
   - PostgreSQL 서비스 실행 여부 확인
   - 연결 URL 확인
   - 데이터베이스 사용자 권한 확인

2. **API 키 오류**
   - 환경 변수 설정 확인
   - API 키 유효성 확인
   - 서비스 할당량 확인

3. **Excel 구성이 적용되지 않음**
   - Excel 파일 형식 확인
   - 파일 경로 확인
   - 변환 로그 확인

## 📄 라이선스

이 프로젝트는 Apache 2.0 라이선스를 따릅니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- [FastAPI](https://fastapi.tiangolo.com/) - 현대적이고 빠른 웹 프레임워크
- [OpenAI](https://openai.com/) - AI 모델 서비스
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/) - 음성 및 감정 분석
- [Google Cloud](https://cloud.google.com/) - 클라우드 서비스 지원

## 📞 지원

질문이나 제안이 있으시면:

1. [Issues](https://github.com/neothan-dev/voice-ai-chat-agent-backend/issues) 확인
2. 새 Issue 생성
3. 유지관리자에게 문의

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!
