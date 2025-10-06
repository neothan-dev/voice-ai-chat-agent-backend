# Copyright © 2025 Neothan
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_DEFAULT = os.getenv("DATABASE_URL_DEFAULT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# HuggingFace API
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Azure 认知服务
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_EMOTION_KEY = os.getenv("AZURE_EMOTION_KEY", "")
AZURE_EMOTION_ENDPOINT = os.getenv("AZURE_EMOTION_ENDPOINT", "")
DEFAULT_TTS_REGION = os.getenv("DEFAULT_TTS_REGION", "eastus")
DEFAULT_TTS_LANG = os.getenv("DEFAULT_TTS_LANG", "en-US")
DEFAULT_STT_REGION = os.getenv("DEFAULT_STT_REGION", "eastus")
DEFAULT_STT_LANG = os.getenv("DEFAULT_STT_LANG", "en-US")
SECRET_KEY = os.getenv("SECRET_KEY")

# Google Cloud API
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# DeepL API
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")

# 翻译服务默认目标语言
DEFAULT_TRANSLATE_TARGET_LANG = os.getenv("DEFAULT_TRANSLATE_TARGET_LANG", "en")

# 设置Google Cloud认证信息到环境变量
if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS 