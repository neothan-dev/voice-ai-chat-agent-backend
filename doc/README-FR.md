# voice-ai-chat-agent-backend

<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/README.md"><img alt="README in English" src="https://img.shields.io/badge/English-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-CN.md"><img alt="简体中文操作指南" src="https://img.shields.io/badge/简体中文-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-JP.md"><img alt="日本語のREADME" src="https://img.shields.io/badge/日本語-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-KR.md"><img alt="README in 한국어" src="https://img.shields.io/badge/한국어-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-ES.md"><img alt="README en Español" src="https://img.shields.io/badge/Español-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-FR.md"><img alt="README en Français" src="https://img.shields.io/badge/Français-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-IT.md"><img alt="README in Italiano" src="https://img.shields.io/badge/Italiano-lightgrey"></a>

Un service backend de chat vocal IA basé sur FastAPI prenant en charge l'interaction vocale en temps réel, la gestion des utilisateurs, la configuration des données et le déploiement dans le cloud.

## ✨ Fonctionnalités

- 🎤 **Interaction vocale en temps réel**: Prend en charge la reconnaissance vocale (STT) et la synthèse vocale (TTS)
- 🤖 **Dialogue IA**: Intègre les modèles OpenAI GPT pour des conversations intelligentes
- 👤 **Gestion des utilisateurs**: Inscription, connexion et gestion des sessions complètes
- 📊 **Configuration des données**: Configuration flexible des données via des fichiers Excel
- 🌐 **Prise en charge WebSocket**: Communication bidirectionnelle en temps réel
- 🚀 **Déploiement en un clic**: Prend en charge le déploiement en un clic sur Google Cloud Run
- 🔧 **Architecture extensible**: Conception modulaire, facile à étendre

## 🏗️ Architecture

```
├── api/                    # Modules de routes API
│   ├── auth.py          # Authentification des utilisateurs
│   ├── ai.py            # Endpoints de conversation IA
│   ├── speech.py        # Traitement de la parole
│   ├── navigation.py    # Fonctionnalités de navigation
│   ├── dashboard.py     # Tableau de bord
│   ├── device.py       # Gestion des appareils
│   └── health.py       # Vérification d'état
├── core/                 # Modules principaux
│   ├── config.py       # Gestion de la configuration
│   └── db.py           # Connexion à la base de données
├── models/              # Modèles de données
│   ├── user.py         # Modèle utilisateur
│   ├── session.py      # Modèle de session
│   └── health_data.py  # Modèle de données de santé
├── services/            # Services métier
│   ├── ai_comprehensive_service.py  # Service IA complet
│   ├── stt_service.py  # Parole en texte
│   ├── tts_service.py  # Texte en parole
│   ├── emotion_service.py  # Analyse des sentiments
│   ├── translation_service.py  # Service de traduction
│   └── ...
├── utils/               # Utilitaires
│   ├── config_manager.py  # Chargeur de configuration
│   └── excel_to_code.py   # Excel vers code
├── dev/data/           # Données de développement
│   ├── excel/          # Fichiers de configuration Excel
│   └── code/           # Code de configuration généré
└── main.py             # Point d'entrée de l'application
```

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.8+
- PostgreSQL 12+
- Diverses clés API de services IA

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
cd voice-ai-chat-agent-backend
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp env_example.txt .env
```

Modifiez le fichier `.env` et configurez les clés API requises :

```env
# Configuration de la base de données
DATABASE_URL=postgresql://postgres:password@localhost:5432/voice_ai_db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Services cognitifs Azure
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_EMOTION_KEY=your_azure_emotion_key_here
AZURE_EMOTION_ENDPOINT=your_azure_emotion_endpoint_here

# API Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=credential/your_google_cloud_credential.json

# Autres paramètres...
```

5. **Initialiser la base de données**
```bash
# Assurez-vous que le service PostgreSQL est en cours d'exécution
# Créer la base de données
createdb voice_ai_db

# Lancer l'application (initialise automatiquement la base)
python main.py
```

6. **Démarrer le service**
```bash
# Mode développement
python main.py

# Ou utiliser uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visitez `http://localhost:8000/docs` pour voir la documentation de l'API.

## 📋 Configuration

### Variables d'environnement

| Nom | Description | Requis |
|--------|-------------|--------|
| `DATABASE_URL` | URL de connexion à la base de données | ✅ |
| `OPENAI_API_KEY` | Clé API OpenAI | ✅ |
| `AZURE_SPEECH_KEY` | Clé du service vocal Azure | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Chemin du fichier d'identifiants Google Cloud | ✅ |
| `SECRET_KEY` | Secret d'authentification JWT | ✅ |
| `HOST` | Hôte du serveur | ❌ |
| `PORT` | Port du serveur | ❌ |
| `DEBUG` | Mode débogage | ❌ |

### Système de configuration Excel

Le projet prend en charge la configuration des données d'application via des fichiers Excel pour une gestion flexible :

1. **Créer des fichiers Excel**: Créez des fichiers `.xlsx` dans `dev/data/excel/`
2. **Configurer les données**: Remplissez les données selon le modèle
3. **Conversion automatique**: Le système convertit automatiquement Excel en code de configuration Python
4. **Chargement dynamique**: Prend en charge le rechargement à chaud; les configurations sont mises à jour après modification d'Excel

#### Utiliser le gestionnaire de configuration

```python
from utils.config_manager import CONFIG_LOADER

# Obtenir une configuration
config = CONFIG_LOADER.get_config('navigation')

# Obtenir la configuration d'une feuille spécifique
sheet_config = CONFIG_LOADER.get_config_sheet('navigation', 'routes')

# Obtenir une valeur de configuration spécifique
value = CONFIG_LOADER.get_config_value('navigation', 'routes', 'home_path')
```

## 🔧 API Endpoints

### Authentification

- `POST /auth/register` - Inscription utilisateur
- `POST /auth/login` - Connexion utilisateur
- `POST /auth/refresh` - Rafraîchir le jeton
- `GET /auth/me` - Obtenir les informations de l'utilisateur courant

### Conversation IA

- `POST /ai/chat` - Envoyer un message
- `WebSocket /ai/chat/ws` - Connexion de chat en temps réel
- `GET /ai/history` - Obtenir l'historique des conversations

### Voix

- `POST /speech/stt` - Parole en texte
- `POST /speech/tts` - Texte en parole
- `WebSocket /speech/ws` - Flux vocal en temps réel

### Navigation

- `GET /navigation/routes` - Obtenir les routes de navigation
- `POST /navigation/update` - Mettre à jour la configuration de navigation

## 🐳 Déploiement Docker

### Exécution locale avec Docker

```bash
# Construire l'image
docker build -t voice-ai-chat-agent-backend .

# Exécuter le conteneur
docker run -p 8000:8000 --env-file .env voice-ai-chat-agent-backend
```

### Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

## ☁️ Déploiement Google Cloud

### Déploiement en un clic

```bash
# Configurer Google Cloud CLI
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Lancer le script de déploiement
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### Déploiement manuel

1. **Construire l'image**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend
```

2. **Déployer sur Cloud Run**
```bash
gcloud run deploy voice-ai-chat-agent-backend \
  --image gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 Tests

```bash
# Exécuter les tests
pytest

# Exécuter un test spécifique
pytest tests/test_auth.py

# Générer le rapport de couverture
pytest --cov=api --cov-report=html
```

## 📊 Supervision et Journalisation

### Configuration des logs

Emplacement du fichier de logs : `logs/app.log`

Le niveau de logs peut être configuré via la variable d'environnement `LOG_LEVEL`.

## 🔒 Considérations de Sécurité

- Authentification par jeton JWT
- Hachage et stockage des mots de passe
- Configuration CORS
- Protection des informations sensibles via des variables d'environnement
- Limitation du débit de l'API (configurable)

## 🤝 Guide de Contribution

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Guide de Développement

### Ajouter un nouvel endpoint API

1. Créez un nouveau fichier de route dans `api/`
2. Enregistrez la route dans `main.py`
3. Ajoutez les modèles de données correspondants (si nécessaire)
4. Écrivez des tests

### Ajouter une nouvelle configuration

1. Créez un fichier Excel dans `dev/data/excel/`
2. Remplissez les données selon le modèle
3. Utilisez `CONFIG_LOADER` pour charger la configuration

### Standards de Code

- Utilisez des annotations de types
- Suivez PEP 8
- Ajoutez des docstrings appropriés
- Écrivez des tests unitaires

## 🐛 Dépannage

### Problèmes courants

1. **Échec de connexion à la base de données**
   - Vérifiez que PostgreSQL est en cours d'exécution
   - Vérifiez l'URL de connexion
   - Confirmez les permissions de l'utilisateur

2. **Erreurs de clé API**
   - Vérifiez la configuration des variables d'environnement
   - Vérifiez la validité des clés
   - Confirmez les quotas du service

3. **Configuration Excel non appliquée**
   - Vérifiez le format du fichier Excel
   - Confirmez le chemin du fichier
   - Consultez les logs de conversion

## 📄 Licence

Ce projet est sous licence Apache 2.0 - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne et rapide
- [OpenAI](https://openai.com/) - Services de modèles IA
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/) - Parole et analyse des sentiments
- [Google Cloud](https://cloud.google.com/) - Support des services cloud

## 📞 Support

Si vous avez des questions ou des suggestions :

1. Consultez [Issues](https://github.com/neothan-dev/voice-ai-chat-agent-backend/issues)
2. Créez un nouvel issue
3. Contactez les mainteneurs

---

⭐ Si ce projet vous aide, merci de lui attribuer une étoile !
