# voice-ai-chat-agent-backend

<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/README.md"><img alt="README in English" src="https://img.shields.io/badge/English-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-CN.md"><img alt="简体中文操作指南" src="https://img.shields.io/badge/简体中文-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-JP.md"><img alt="日本語のREADME" src="https://img.shields.io/badge/日本語-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-KR.md"><img alt="README in 한국어" src="https://img.shields.io/badge/한국어-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-ES.md"><img alt="README en Español" src="https://img.shields.io/badge/Español-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-FR.md"><img alt="README en Français" src="https://img.shields.io/badge/Français-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-IT.md"><img alt="README in Italiano" src="https://img.shields.io/badge/Italiano-lightgrey"></a>

Un servicio backend de chat de voz con IA basado en FastAPI que admite interacción de voz en tiempo real, gestión de usuarios, configuración de datos y despliegue en la nube.

## ✨ Características

- 🎤 **Interacción de voz en tiempo real**: Soporta Reconocimiento de Voz (STT) y Síntesis de Voz (TTS)
- 🤖 **Chat con IA**: Integra modelos OpenAI GPT para conversaciones inteligentes
- 👤 **Gestión de usuarios**: Registro, inicio de sesión y gestión de sesiones completos
- 📊 **Configuración de datos**: Configuración flexible de datos de la aplicación mediante archivos Excel
- 🌐 **Soporte WebSocket**: Comunicación bidireccional en tiempo real
- 🚀 **Despliegue con un clic**: Soporta despliegue con un clic en Google Cloud Run
- 🔧 **Arquitectura extensible**: Diseño modular, fácil de ampliar

## 🏗️ Arquitectura

```
├── api/                    # Módulos de rutas de API
│   ├── auth.py          # Autenticación de usuarios
│   ├── ai.py            # Endpoints de conversación IA
│   ├── speech.py        # Procesamiento de voz
│   ├── navigation.py    # Funciones de navegación
│   ├── dashboard.py     # Tablero
│   ├── device.py       # Gestión de dispositivos
│   └── health.py       # Comprobación de estado
├── core/                 # Módulos centrales
│   ├── config.py       # Gestión de configuración
│   └── db.py           # Conexión a base de datos
├── models/              # Modelos de datos
│   ├── user.py         # Modelo de usuario
│   ├── session.py      # Modelo de sesión
│   └── health_data.py  # Modelo de datos de salud
├── services/            # Servicios de negocio
│   ├── ai_comprehensive_service.py  # Servicio integral de IA
│   ├── stt_service.py  # Voz a texto
│   ├── tts_service.py  # Texto a voz
│   ├── emotion_service.py  # Análisis de sentimientos
│   ├── translation_service.py  # Servicio de traducción
│   └── ...
├── utils/               # Utilidades
│   ├── config_manager.py  # Cargador de configuración
│   └── excel_to_code.py   # Excel a código
├── dev/data/           # Datos de desarrollo
│   ├── excel/          # Archivos de configuración Excel
│   └── code/           # Código de configuración generado
└── main.py             # Punto de entrada de la aplicación
```

## 🚀 Inicio Rápido

### Requisitos

- Python 3.8+
- PostgreSQL 12+
- Varias claves API de servicios de IA

### Pasos de Instalación

1. **Clonar el proyecto**
```bash
git clone https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
cd voice-ai-chat-agent-backend
```

2. **Crear un entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# O
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp env_example.txt .env
```

Edite el archivo `.env` y configure las claves API necesarias:

```env
# Configuración de base de datos
DATABASE_URL=postgresql://postgres:password@localhost:5432/voice_ai_db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Servicios Cognitivos de Azure
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_EMOTION_KEY=your_azure_emotion_key_here
AZURE_EMOTION_ENDPOINT=your_azure_emotion_endpoint_here

# API de Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=credential/your_google_cloud_credential.json

# Otros ajustes...
```

5. **Inicializar la base de datos**
```bash
# Asegúrese de que el servicio de PostgreSQL esté en ejecución
# Crear la base de datos
createdb voice_ai_db

# Ejecutar la aplicación (inicializa la base de datos automáticamente)
python main.py
```

6. **Iniciar el servicio**
```bash
# Modo desarrollo
python main.py

# O use uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visite `http://localhost:8000/docs` para ver la documentación de la API.

## 📋 Configuración

### Variables de entorno

| Nombre | Descripción | Requerido |
|--------|-------------|-----------|
| `DATABASE_URL` | URL de conexión a la base de datos | ✅ |
| `OPENAI_API_KEY` | Clave API de OpenAI | ✅ |
| `AZURE_SPEECH_KEY` | Clave del servicio de voz de Azure | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Ruta del archivo de credenciales de Google Cloud | ✅ |
| `SECRET_KEY` | Secreto de autenticación JWT | ✅ |
| `HOST` | Host del servidor | ❌ |
| `PORT` | Puerto del servidor | ❌ |
| `DEBUG` | Modo de depuración | ❌ |

### Sistema de configuración con Excel

El proyecto permite configurar datos de la aplicación mediante archivos Excel para una gestión flexible:

1. **Crear archivos Excel**: Cree archivos `.xlsx` en `dev/data/excel/`
2. **Configurar datos**: Rellene los datos siguiendo el formato de la plantilla
3. **Conversión automática**: El sistema convierte automáticamente Excel a código de configuración en Python
4. **Carga dinámica**: Soporta recarga en caliente; las configuraciones se actualizan tras modificar el Excel

#### Uso del gestor de configuración

```python
from utils.config_manager import CONFIG_LOADER

# Obtener una configuración
config = CONFIG_LOADER.get_config('navigation')

# Obtener la configuración de una hoja específica
sheet_config = CONFIG_LOADER.get_config_sheet('navigation', 'routes')

# Obtener un valor de configuración específico
value = CONFIG_LOADER.get_config_value('navigation', 'routes', 'home_path')
```

## 🔧 Endpoints de la API

### Autenticación

- `POST /auth/register` - Registro de usuarios
- `POST /auth/login` - Inicio de sesión
- `POST /auth/refresh` - Renovar token
- `GET /auth/me` - Obtener información del usuario actual

### Conversación IA

- `POST /ai/chat` - Enviar mensaje de chat
- `WebSocket /ai/chat/ws` - Conexión de chat en tiempo real
- `GET /ai/history` - Obtener historial de chat

### Voz

- `POST /speech/stt` - Voz a texto
- `POST /speech/tts` - Texto a voz
- `WebSocket /speech/ws` - Flujo de voz en tiempo real

### Navegación

- `GET /navigation/routes` - Obtener rutas de navegación
- `POST /navigation/update` - Actualizar configuración de navegación

## 🐳 Despliegue con Docker

### Ejecutar localmente con Docker

```bash
# Construir imagen
docker build -t voice-ai-chat-agent-backend .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env voice-ai-chat-agent-backend
```

### Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## ☁️ Despliegue en Google Cloud

### Despliegue con un clic

```bash
# Configurar Google Cloud CLI
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Ejecutar el script de despliegue
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### Despliegue manual

1. **Construir la imagen**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend
```

2. **Desplegar en Cloud Run**
```bash
gcloud run deploy voice-ai-chat-agent-backend \
  --image gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 Pruebas

```bash
# Ejecutar pruebas
pytest

# Ejecutar una prueba específica
pytest tests/test_auth.py

# Generar reporte de cobertura
pytest --cov=api --cov-report=html
```

## 📊 Monitoreo y Registro

### Configuración de logs

Ubicación del archivo de logs: `logs/app.log`

El nivel de logs se puede configurar mediante la variable de entorno `LOG_LEVEL`.

## 🔒 Consideraciones de Seguridad

- Autenticación con tokens JWT
- Cifrado y almacenamiento de contraseñas
- Configuración de CORS
- Protección de información sensible con variables de entorno
- Limitación de tasa de API (configurable)

## 🤝 Guía de Contribución

1. Haga un Fork del repositorio
2. Cree una rama de funcionalidad (`git checkout -b feature/AmazingFeature`)
3. Realice commits (`git commit -m 'Add some AmazingFeature'`)
4. Empuje la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request

## 📝 Guía de Desarrollo

### Agregar un nuevo endpoint de API

1. Cree un nuevo archivo de ruta en `api/`
2. Registre la ruta en `main.py`
3. Agregue los modelos de datos correspondientes (si es necesario)
4. Escriba casos de prueba

### Agregar una nueva configuración

1. Cree un archivo Excel en `dev/data/excel/`
2. Configure los datos siguiendo el formato de la plantilla
3. Use `CONFIG_LOADER` para cargar la configuración

### Estándares de Código

- Use anotaciones de tipo
- Siga PEP 8
- Agregue docstrings apropiados
- Escriba pruebas unitarias

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Falla de conexión a la base de datos**
   - Verifique si el servicio de PostgreSQL está en ejecución
   - Verifique la URL de conexión
   - Confirme permisos del usuario de la base

2. **Errores de claves API**
   - Revise la configuración de variables de entorno
   - Verifique la validez de las claves
   - Confirme cuotas del servicio

3. **Configuración de Excel no aplicada**
   - Revise el formato del archivo Excel
   - Confirme la ruta correcta del archivo
   - Revise los logs de conversión

## 📄 Licencia

Este proyecto está bajo la licencia Apache 2.0 - vea el archivo [LICENSE](LICENSE) para más detalles.

Apache 2.0 proporciona:
- ✅ Protección de patentes
- ✅ Protección de marcas  
- ✅ Salvaguardas legales más fuertes
- ✅ Estándares de nivel empresarial

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno y rápido
- [OpenAI](https://openai.com/) - Servicios de modelos de IA
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/) - Voz y análisis de sentimientos
- [Google Cloud](https://cloud.google.com/) - Soporte de servicios en la nube

## 📞 Soporte

Si tiene preguntas o sugerencias:

1. Revise [Issues](https://github.com/neothan-dev/voice-ai-chat-agent-backend/issues)
2. Cree un nuevo Issue
3. Contacte a los mantenedores

---

⭐ ¡Si este proyecto le ayuda, por favor déle una estrella!
