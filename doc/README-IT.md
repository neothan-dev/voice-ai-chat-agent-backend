# voice-ai-chat-agent-backend

<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/README.md"><img alt="README in English" src="https://img.shields.io/badge/English-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-CN.md"><img alt="简体中文操作指南" src="https://img.shields.io/badge/简体中文-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-JP.md"><img alt="日本語のREADME" src="https://img.shields.io/badge/日本語-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-KR.md"><img alt="README in 한국어" src="https://img.shields.io/badge/한국어-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-ES.md"><img alt="README en Español" src="https://img.shields.io/badge/Español-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-FR.md"><img alt="README en Français" src="https://img.shields.io/badge/Français-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-IT.md"><img alt="README in Italiano" src="https://img.shields.io/badge/Italiano-lightgrey"></a>

Un servizio backend di chat vocale IA basato su FastAPI che supporta interazione vocale in tempo reale, gestione utenti, configurazione dei dati e distribuzione su cloud.

## ✨ Caratteristiche

- 🎤 **Interazione vocale in tempo reale**: Supporta Riconoscimento Vocale (STT) e Sintesi Vocale (TTS)
- 🤖 **Chat IA**: Integra modelli OpenAI GPT per conversazioni intelligenti
- 👤 **Gestione utenti**: Registrazione, login e gestione sessioni complete
- 📊 **Configurazione dati**: Configurazione flessibile dei dati tramite file Excel
- 🌐 **Supporto WebSocket**: Comunicazione bidirezionale in tempo reale
- 🚀 **Deploy con un clic**: Supporta deploy con un clic su Google Cloud Run
- 🔧 **Architettura estensibile**: Design modulare, facile da estendere

## 🏗️ Architettura

```
├── api/                    # Moduli di routing API
│   ├── auth.py          # Autenticazione utente
│   ├── ai.py            # Endpoint conversazione IA
│   ├── speech.py        # Elaborazione vocale
│   ├── navigation.py    # Funzioni di navigazione
│   ├── dashboard.py     # Dashboard
│   ├── device.py       # Gestione dispositivi
│   └── health.py       # Controllo stato
├── core/                 # Moduli core
│   ├── config.py       # Gestione configurazione
│   └── db.py           # Connessione al database
├── models/              # Modelli dati
│   ├── user.py         # Modello utente
│   ├── session.py      # Modello sessione
│   └── health_data.py  # Modello dati salute
├── services/            # Servizi di business
│   ├── ai_comprehensive_service.py  # Servizio IA completo
│   ├── stt_service.py  # Voce a testo
│   ├── tts_service.py  # Testo a voce
│   ├── emotion_service.py  # Analisi sentimenti
│   ├── translation_service.py  # Servizio traduzione
│   └── ...
├── utils/               # Utilità
│   ├── config_manager.py  # Loader configurazione
│   └── excel_to_code.py   # Excel a codice
├── dev/data/           # Dati di sviluppo
│   ├── excel/          # File di configurazione Excel
│   └── code/           # Codice di configurazione generato
└── main.py             # Entrypoint applicazione
```

## 🚀 Guida Rapida

### Requisiti

- Python 3.8+
- PostgreSQL 12+
- Varie chiavi API di servizi IA

### Passi di Installazione

1. **Clonare il progetto**
```bash
git clone https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
cd voice-ai-chat-agent-backend
```

2. **Creare un ambiente virtuale**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Oppure
venv\Scripts\activate  # Windows
```

3. **Installare le dipendenze**
```bash
pip install -r requirements.txt
```

4. **Configurare le variabili d'ambiente**
```bash
cp env_example.txt .env
```

Modificare `.env` e configurare le chiavi API richieste:

```env
# Configurazione database
DATABASE_URL=postgresql://postgres:password@localhost:5432/voice_ai_db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Servizi Cognitivi Azure
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_EMOTION_KEY=your_azure_emotion_key_here
AZURE_EMOTION_ENDPOINT=your_azure_emotion_endpoint_here

# API Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=credential/your_google_cloud_credential.json

# Altre impostazioni...
```

5. **Inizializzare il database**
```bash
# Assicurarsi che PostgreSQL sia in esecuzione
# Creare il database
createdb voice_ai_db

# Avviare l'app (inizializza automaticamente il database)
python main.py
```

6. **Avviare il servizio**
```bash
# Modalità sviluppo
python main.py

# Oppure usare uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visitare `http://localhost:8000/docs` per la documentazione API.

## 📋 Configurazione

### Variabili d'Ambiente

| Nome | Descrizione | Richiesto |
|--------|-------------|-----------|
| `DATABASE_URL` | URL di connessione al database | ✅ |
| `OPENAI_API_KEY` | Chiave API OpenAI | ✅ |
| `AZURE_SPEECH_KEY` | Chiave del servizio vocale Azure | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Percorso del file credenziali Google Cloud | ✅ |
| `SECRET_KEY` | Segreto di autenticazione JWT | ✅ |
| `HOST` | Host del server | ❌ |
| `PORT` | Porta del server | ❌ |
| `DEBUG` | Modalità debug | ❌ |

### Sistema di Configurazione Excel

Il progetto supporta la configurazione dei dati tramite file Excel per una gestione flessibile:

1. **Creare file Excel**: Creare file `.xlsx` in `dev/data/excel/`
2. **Configurare i dati**: Compilare i dati secondo il modello
3. **Conversione automatica**: Il sistema converte automaticamente Excel in codice di configurazione Python
4. **Caricamento dinamico**: Supporta hot reload; la configurazione si aggiorna dopo modifiche a Excel

#### Utilizzo del loader di configurazione

```python
from utils.config_manager import CONFIG_LOADER

# Ottenere una configurazione
config = CONFIG_LOADER.get_config('navigation')

# Ottenere la configurazione di un foglio specifico
sheet_config = CONFIG_LOADER.get_config_sheet('navigation', 'routes')

# Ottenere un valore specifico
value = CONFIG_LOADER.get_config_value('navigation', 'routes', 'home_path')
```

## 🔧 Endpoint API

### Autenticazione

- `POST /auth/register` - Registrazione utente
- `POST /auth/login` - Login utente
- `POST /auth/refresh` - Refresh token
- `GET /auth/me` - Informazioni utente corrente

### Conversazione IA

- `POST /ai/chat` - Invia messaggio
- `WebSocket /ai/chat/ws` - Connessione chat in tempo reale
- `GET /ai/history` - Cronologia chat

### Voce

- `POST /speech/stt` - Voce a testo
- `POST /speech/tts` - Testo a voce
- `WebSocket /speech/ws` - Stream vocale in tempo reale

### Navigazione

- `GET /navigation/routes` - Ottenere rotte di navigazione
- `POST /navigation/update` - Aggiornare configurazione navigazione

## 🐳 Deploy Docker

### Esecuzione locale con Docker

```bash
# Build immagine
docker build -t voice-ai-chat-agent-backend .

# Esegui container
docker run -p 8000:8000 --env-file .env voice-ai-chat-agent-backend
```

### Docker Compose

```bash
# Avvia tutti i servizi
docker-compose up -d

# Vedi i log
docker-compose logs -f
```

## ☁️ Deploy su Google Cloud

### Deploy con un clic

```bash
# Configurare Google Cloud CLI
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Eseguire lo script di deploy
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### Deploy manuale

1. **Build immagine**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend
```

2. **Deploy su Cloud Run**
```bash
gcloud run deploy voice-ai-chat-agent-backend \
  --image gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 Test

```bash
# Esegui test
pytest

# Esegui test specifico
pytest tests/test_auth.py

# Genera report di copertura
pytest --cov=api --cov-report=html
```

## 📊 Monitoraggio e Log

### Configurazione dei log

Percorso file log: `logs/app.log`

Il livello di log può essere configurato tramite la variabile d'ambiente `LOG_LEVEL`.

## 🔒 Considerazioni sulla Sicurezza

- Autenticazione token JWT
- Cifratura e archiviazione delle password
- Configurazione CORS
- Protezione delle informazioni sensibili con variabili d'ambiente
- Limitazione del rate API (configurabile)

## 🤝 Guida ai Contributi

1. Fai Fork del progetto
2. Crea un branch di feature (`git checkout -b feature/AmazingFeature`)
3. Fai commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push del branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 Guida allo Sviluppo

### Aggiungere un nuovo endpoint API

1. Crea un nuovo file di route in `api/`
2. Registra la route in `main.py`
3. Aggiungi i modelli dati (se necessario)
4. Scrivi i test

### Aggiungere una nuova configurazione

1. Crea un file Excel in `dev/data/excel/`
2. Compila i dati secondo il modello
3. Usa `CONFIG_LOADER` per caricare la configurazione

### Standard di Codice

- Usa type hints
- Segui PEP 8
- Aggiungi docstring adeguate
- Scrivi unit test

## 🐛 Risoluzione dei Problemi

### Problemi Comuni

1. **Connessione al database fallita**
   - Verifica che PostgreSQL sia in esecuzione
   - Verifica l'URL di connessione
   - Conferma i permessi utente

2. **Errori chiavi API**
   - Controlla la configurazione delle variabili d'ambiente
   - Verifica la validità delle chiavi
   - Conferma le quote del servizio

3. **Configurazione Excel non applicata**
   - Verifica il formato del file Excel
   - Conferma il percorso corretto
   - Controlla i log di conversione

## 📄 Licenza

Questo progetto è concesso sotto licenza Apache 2.0 - vedere [LICENSE](LICENSE) per dettagli.

Apache 2.0 fornisce:
- ✅ Protezione dei brevetti
- ✅ Protezione del marchio  
- ✅ Tutele legali più solide
- ✅ Standard a livello enterprise

## 🙏 Ringraziamenti

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno e veloce
- [OpenAI](https://openai.com/) - Servizi di modelli IA
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/) - Voce e analisi sentimenti
- [Google Cloud](https://cloud.google.com/) - Supporto servizi cloud

## 📞 Supporto

Se hai domande o suggerimenti:

1. Consulta [Issues](https://github.com/neothan-dev/voice-ai-chat-agent-backend/issues)
2. Crea un nuovo Issue
3. Contatta i manutentori

---

⭐ Se questo progetto ti è utile, dagli una stella!
