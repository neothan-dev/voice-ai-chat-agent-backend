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
import tempfile
import wave
import re
from typing import Tuple, Optional, Dict, List
import requests
from loguru import logger
import random

# 配置
from core.config import OPENAI_API_KEY, AZURE_SPEECH_KEY, DEFAULT_STT_REGION, DEFAULT_STT_LANG

# 支持的语言配置
SUPPORTED_LANGUAGES = {
    "zh": {
        "name": "中文",
        "google_code": "zh-CN",
        "azure_code": "zh-CN",
        "openai_code": "zh",
        "confidence_threshold": 0.7
    },
    "en": {
        "name": "English",
        "google_code": "en-US",
        "azure_code": "en-US",
        "openai_code": "en",
        "confidence_threshold": 0.7
    },
    "ja": {
        "name": "日本語",
        "google_code": "ja-JP",
        "azure_code": "ja-JP",
        "openai_code": "ja",
        "confidence_threshold": 0.7
    },
    "ko": {
        "name": "한국어",
        "google_code": "ko-KR",
        "azure_code": "ko-KR",
        "openai_code": "ko",
        "confidence_threshold": 0.7
    },
    "fr": {
        "name": "Français",
        "google_code": "fr-FR",
        "azure_code": "fr-FR",
        "openai_code": "fr",
        "confidence_threshold": 0.7
    },
    "de": {
        "name": "Deutsch",
        "google_code": "de-DE",
        "azure_code": "de-DE",
        "openai_code": "de",
        "confidence_threshold": 0.7
    },
    "es": {
        "name": "Español",
        "google_code": "es-ES",
        "azure_code": "es-ES",
        "openai_code": "es",
        "confidence_threshold": 0.7
    },
    "ru": {
        "name": "Русский",
        "google_code": "ru-RU",
        "azure_code": "ru-RU",
        "openai_code": "ru",
        "confidence_threshold": 0.7
    },
    "ar": {
        "name": "العربية",
        "google_code": "ar-SA",
        "azure_code": "ar-SA",
        "openai_code": "ar",
        "confidence_threshold": 0.6
    },
    "hi": {
        "name": "हिन्दी",
        "google_code": "hi-IN",
        "azure_code": "hi-IN",
        "openai_code": "hi",
        "confidence_threshold": 0.6
    }
}

# 语言检测缓存
language_detection_cache = {}

def stt_stream(audio_chunk: bytes, preferred_language: Optional[str] = None) -> Tuple[bool, str, str, str]:
    """
    多语言语音转文本服务
    Args:
        audio_chunk: 音频数据字节流
        preferred_language: 用户偏好的语言代码
    Returns:
        (succ, text, lang, method): 识别的文本、语言代码和使用的服务
    """
    try:
        # 保存音频到临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_chunk)
            temp_file_path = temp_file.name
        
        # # 1. 首先尝试使用用户偏好语言进行识别
        # if preferred_language and preferred_language in SUPPORTED_LANGUAGES:
        #     text, lang = _try_stt_with_language(temp_file_path, preferred_language)
        #     if text:
        #         return True, text, lang, f"preferred_{preferred_language}"
        
        # 2. 尝试Google Speech API（支持自动语言检测）
        text, lang = _try_google_speech_enhanced(temp_file_path)
        if text:
            return True, text, lang, "google"
        else:
            print("【API Service Failed!】Google语音转文本失败!")
        
        # # 3. 尝试OpenAI Whisper（支持多语言）
        # text, lang = _try_openai_whisper_enhanced(temp_file_path)
        # if text:
        #     return True, text, lang, "openai"
        # else:
        #     print("【API Service Failed!】OpenAI Whisper语音转文本失败!")
            
        # # 4. 尝试Azure Speech Services（支持自动语言检测）
        # text, lang = _try_azure_speech_enhanced(temp_file_path)
        # if text:
        #     return True, text, lang, "azure"
        # else:
        #     print("【API Service Failed!】Azure语音转文本失败!")
            
        # 5. 如果所有服务都失败，使用智能备用方案
        text, lang = _intelligent_fallback_stt(audio_chunk)
        return False, text, lang, "intelligent_fallback"
        
    except Exception as e:
        logger.error(f"STT处理失败: {e}")
        text, lang = _intelligent_fallback_stt(audio_chunk)
        return False, text, lang, "fallback"
    finally:
        # 清理临时文件
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass

def _try_stt_with_language(audio_path: str, language: str) -> Tuple[Optional[str], str]:
    """
    使用指定语言进行STT识别
    """
    try:
        # 获取语言配置
        lang_config = SUPPORTED_LANGUAGES.get(language)
        if not lang_config:
            return None, language
        
        # 尝试Google Speech API
        text, detected_lang = _try_google_speech_with_language(audio_path, lang_config["google_code"])
        if text:
            return text, detected_lang
        
        # 尝试Azure Speech API
        text, detected_lang = _try_azure_speech_with_language(audio_path, lang_config["azure_code"])
        if text:
            return text, detected_lang
        
        # 尝试OpenAI Whisper
        text, detected_lang = _try_openai_whisper_with_language(audio_path, lang_config["openai_code"])
        if text:
            return text, detected_lang
        
        return None, language
        
    except Exception as e:
        logger.warning(f"指定语言STT失败 ({language}): {e}")
        return None, language

def _try_google_speech_enhanced(audio_path: str) -> Tuple[Optional[str], str]:
    """增强的Google Cloud Speech API（支持多语言自动检测）"""
    try:
        from google.cloud import speech
        
        client = speech.SpeechClient()
        
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        
        # 尝试多种语言配置进行识别
        # supported_languages = ["en-US", "zh-CN", "ja-JP", "ko-KR", "fr-FR", 
        #                       "de-DE", "es-ES", "ru-RU", "ar-SA", "hi-IN"]
        supported_languages = ["en-US"]
        
        for lang_code in supported_languages:
            try:
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code=lang_code,
                    enable_automatic_punctuation=True,
                )
                
                response = client.recognize(config=config, audio=audio)
                
                if response.results:
                    result = response.results[0]
                    text = result.alternatives[0].transcript
                    
                    # 转换语言代码格式
                    lang = _normalize_language_code(lang_code)
                    
                    # 验证语言置信度
                    if _validate_language_detection(text, lang):
                        return text, lang
                        
            except Exception as e:
                logger.debug(f"Google Speech语言 {lang_code} 识别失败: {e}")
                continue
        
        return None, None
        
    except Exception as e:
        logger.warning(f"Google Speech增强版失败: {e}")
        return None, None

def _try_openai_whisper_enhanced(audio_path: str) -> Tuple[Optional[str], str]:
    """增强的OpenAI Whisper API（支持多语言）"""
    if not OPENAI_API_KEY:
        return None, None
    
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=None,  # 自动检测语言
                response_format="json"
            )
        
        # 解析响应
        if hasattr(response, 'text') and response.text:
            text = response.text.strip()
            
            # 获取检测到的语言（如果支持）
            try:
                detected_lang = getattr(response, 'language', 'zh')
                lang = _normalize_language_code(detected_lang)
            except:
                # 如果无法获取语言信息，使用文本特征检测
                lang = _detect_language_from_text(text)
            
            # 验证语言检测结果
            if _validate_language_detection(text, lang):
                return text, lang
        
        return None, None
        
    except Exception as e:
        logger.warning(f"OpenAI Whisper增强版失败: {e}")
        return None, None

def _detect_language_from_text(text: str) -> str:
    """从文本特征检测语言"""
    import re
    
    # 中文字符检测
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    if len(chinese_chars) > 0:
        return "zh"
    
    # 日文字符检测
    japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', text)
    if len(japanese_chars) > 0:
        return "ja"
    
    # 韩文字符检测
    korean_chars = re.findall(r'[\uac00-\ud7af]', text)
    if len(korean_chars) > 0:
        return "ko"
    
    # 阿拉伯文字符检测
    arabic_chars = re.findall(r'[\u0600-\u06ff]', text)
    if len(arabic_chars) > 0:
        return "ar"
    
    # 印地文字符检测
    hindi_chars = re.findall(r'[\u0900-\u097f]', text)
    if len(hindi_chars) > 0:
        return "hi"
    
    # 俄文字符检测
    russian_chars = re.findall(r'[\u0400-\u04ff]', text)
    if len(russian_chars) > 0:
        return "ru"
    
    # 德文字符检测（特殊字符）
    german_chars = re.findall(r'[äöüßÄÖÜ]', text)
    if len(german_chars) > 0:
        return "de"
    
    # 法文字符检测（特殊字符）
    french_chars = re.findall(r'[àâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]', text)
    if len(french_chars) > 0:
        return "fr"
    
    # 西班牙文字符检测（特殊字符）
    spanish_chars = re.findall(r'[ñáéíóúüÑÁÉÍÓÚÜ]', text)
    if len(spanish_chars) > 0:
        return "es"
    
    # 默认为英文
    return "en"

def _try_azure_speech_enhanced(audio_path: str) -> Tuple[Optional[str], str]:
    """增强的Azure Speech Services（支持多语言识别）"""
    if not AZURE_SPEECH_KEY:
        return None, None
    
    try:
        import azure.cognitiveservices.speech as speechsdk
        
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY, 
            region=DEFAULT_STT_REGION
        )
        
        audio_config = speechsdk.AudioConfig(filename=audio_path)
        
        # 尝试多种语言进行识别
        supported_languages = ["zh-CN", "en-US", "ja-JP", "ko-KR", "fr-FR", 
                              "de-DE", "es-ES", "ru-RU", "ar-SA", "hi-IN"]
        
        for lang_code in supported_languages:
            try:
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=speech_config, 
                    audio_config=audio_config,
                    language=lang_code
                )
                
                result = speech_recognizer.recognize_once_async().get()
                
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    text = result.text
                    
                    # 转换语言代码格式
                    lang = _normalize_language_code(lang_code)
                    
                    # 验证语言检测结果
                    if _validate_language_detection(text, lang):
                        return text, lang
                        
            except Exception as e:
                logger.debug(f"Azure Speech语言 {lang_code} 识别失败: {e}")
                continue
        
        return None, None
        
    except Exception as e:
        logger.warning(f"Azure Speech增强版失败: {e}")
        return None, None

def _try_google_speech_with_language(audio_path: str, language_code: str) -> Tuple[Optional[str], str]:
    """使用指定语言的Google Speech API"""
    try:
        from google.cloud import speech
        
        client = speech.SpeechClient()
        
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        response = client.recognize(config=config, audio=audio)
        
        if response.results:
            text = response.results[0].alternatives[0].transcript
            return text, _normalize_language_code(language_code)
        
        return None, None
        
    except Exception as e:
        logger.warning(f"Google Speech指定语言失败 ({language_code}): {e}")
        return None, None

def _try_azure_speech_with_language(audio_path: str, language_code: str) -> Tuple[Optional[str], str]:
    """使用指定语言的Azure Speech API"""
    if not AZURE_SPEECH_KEY:
        return None, None
    
    try:
        import azure.cognitiveservices.speech as speechsdk
        
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY, 
            region=DEFAULT_STT_REGION
        )
        
        audio_config = speechsdk.AudioConfig(filename=audio_path)
        
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config,
            language=language_code
        )
        
        result = speech_recognizer.recognize_once_async().get()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = result.text
            return text, _normalize_language_code(language_code)
        
        return None, None
        
    except Exception as e:
        logger.warning(f"Azure Speech指定语言失败 ({language_code}): {e}")
        return None, None

def _try_openai_whisper_with_language(audio_path: str, language_code: str) -> Tuple[Optional[str], str]:
    """使用指定语言的OpenAI Whisper API"""
    if not OPENAI_API_KEY:
        return None, None
    
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language_code
            )
        
        text = response.text.strip()
        return text, _normalize_language_code(language_code) if text else None
        
    except Exception as e:
        logger.warning(f"OpenAI Whisper指定语言失败 ({language_code}): {e}")
        return None, None

def _normalize_language_code(language_code: str) -> str:
    """标准化语言代码"""
    # 语言代码映射
    code_mapping = {
        "zh-CN": "zh", "zh-TW": "zh", "zh": "zh",
        "en-US": "en", "en-GB": "en", "en": "en",
        "ja-JP": "ja", "ja": "ja",
        "ko-KR": "ko", "ko": "ko",
        "fr-FR": "fr", "fr": "fr",
        "de-DE": "de", "de": "de",
        "es-ES": "es", "es": "es",
        "ru-RU": "ru", "ru": "ru",
        "ar-SA": "ar", "ar": "ar",
        "hi-IN": "hi", "hi": "hi"
    }
    
    return code_mapping.get(language_code, "zh")

def _validate_language_detection(text: str, detected_lang: str) -> bool:
    """验证语言检测结果的准确性"""
    if not text or not detected_lang:
        return False
    
    # 基于文本特征的语言验证
    if detected_lang == "zh":
        # 检查是否包含中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return len(chinese_chars) > 0
    elif detected_lang == "ja":
        # 检查是否包含日文字符
        japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', text)
        return len(japanese_chars) > 0
    elif detected_lang == "ko":
        # 检查是否包含韩文字符
        korean_chars = re.findall(r'[\uac00-\ud7af]', text)
        return len(korean_chars) > 0
    elif detected_lang == "ar":
        # 检查是否包含阿拉伯文字符
        arabic_chars = re.findall(r'[\u0600-\u06ff]', text)
        return len(arabic_chars) > 0
    elif detected_lang == "hi":
        # 检查是否包含印地文字符
        hindi_chars = re.findall(r'[\u0900-\u097f]', text)
        return len(hindi_chars) > 0
    else:
        # 其他语言（英文、法文、德文、西班牙文、俄文）
        # 检查是否包含该语言的常见字符
        return len(text.strip()) > 0

def _intelligent_fallback_stt(audio_chunk: bytes) -> Tuple[str, str]:

    sentence = [
        "Sorry, my ears just went on vacation—could you run that by me again?",
        "Oops, my brain just buffered… mind hitting repeat?",
        "Sorry, my ears were on coffee break—could you say that again?",
        "Wait… was that English or did my brain just auto-translate it to gibberish?",
        "Oops, my attention span just tripped over itself—mind repeating?",
        "Sorry, my ears were buffering like bad Wi-Fi—could you reload that?",
        "Hold on, my mental subtitles didn’t show up—could you rerun that scene?",
        "Wait, I think I was momentarily tuned into another frequency—could you say it again?",
        "Sorry, my ears just blinked—can you rewind?"
        "Oops, my listening app just crashed—can you restart the sentence?",
        "Hold up, my brain was lagging—mind hitting refresh?",
        "Sorry, my ears went into airplane mode—could you repeat that?",
        "Wait, my brain’s GPS lost signal—where were we again?",
        "Oops, I think my ears muted themselves—could you unmute?",
        "My brain skipped that like a scratched CD—can you play it again?",
        "Sorry, I was daydreaming in another dimension—what did you say?",
        "Hold on, my mind just took a coffee break—could you repeat?",
        "Oops, that went in one ear and got lost in traffic—say it again?",
    ]

    return random.choice(sentence), "en"

    # """智能备用STT实现，基于音频特征和模式识别"""
    # try:
    #     # 解析WAV文件头
    #     if len(audio_chunk) < 44:
    #         return "你好", "zh"
        
    #     if audio_chunk[:4] != b'RIFF' or audio_chunk[8:12] != b'WAVE':
    #         return "你好", "zh"
        
    #     # 计算音频时长
    #     sample_rate = 16000
    #     bits_per_sample = 16
    #     channels = 1
    #     data_size = len(audio_chunk) - 44
    #     duration = data_size / (sample_rate * bits_per_sample * channels / 8)
        
    #     # 基于音频特征的语言检测
    #     detected_lang = _detect_language_from_audio_features(audio_chunk)
        
    #     # 根据语言和时长生成相应的模拟文本
    #     fallback_texts = {
    #         "zh": {
    #             "short": "你好",
    #             "medium": "今天天气怎么样",
    #             "long": "我想了解健康建议"
    #         },
    #         "en": {
    #             "short": "Hello",
    #             "medium": "How is the weather today",
    #             "long": "I want to know about health advice"
    #         },
    #         "ja": {
    #             "short": "こんにちは",
    #             "medium": "今日の天気はどうですか",
    #             "long": "健康アドバイスについて知りたいです"
    #         },
    #         "ko": {
    #             "short": "안녕하세요",
    #             "medium": "오늘 날씨는 어때요",
    #             "long": "건강 조언에 대해 알고 싶습니다"
    #         },
    #         "fr": {
    #             "short": "Bonjour",
    #             "medium": "Comment est le temps aujourd'hui",
    #             "long": "Je veux connaître les conseils de santé"
    #         },
    #         "de": {
    #             "short": "Hallo",
    #             "medium": "Wie ist das Wetter heute",
    #             "long": "Ich möchte Gesundheitsberatung wissen"
    #         },
    #         "es": {
    #             "short": "Hola",
    #             "medium": "¿Cómo está el clima hoy",
    #             "long": "Quiero saber sobre consejos de salud"
    #         },
    #         "ru": {
    #             "short": "Привет",
    #             "medium": "Какая погода сегодня",
    #             "long": "Я хочу узнать о советах по здоровью"
    #         },
    #         "ar": {
    #             "short": "مرحبا",
    #             "medium": "كيف الطقس اليوم",
    #             "long": "أريد أن أعرف عن النصائح الصحية"
    #         },
    #         "hi": {
    #             "short": "नमस्ते",
    #             "medium": "आज मौसम कैसा है",
    #             "long": "मैं स्वास्थ्य सलाह के बारे में जानना चाहता हूं"
    #         }
    #     }
        
    #     # 确定文本长度类型
    #     if duration < 1.0:
    #         length_type = "short"
    #     elif duration < 2.5:
    #         length_type = "medium"
    #     else:
    #         length_type = "long"
        
    #     # 获取对应语言的文本
    #     lang_texts = fallback_texts.get(detected_lang, fallback_texts["zh"])
    #     text = lang_texts.get(length_type, lang_texts["short"])
        
    #     return text, detected_lang
        
    # except Exception as e:
    #     logger.error(f"智能备用STT失败: {e}")
    #     return "你好", "en"

def _detect_language_from_audio_features(audio_chunk: bytes) -> str:
    """从音频特征检测语言"""
    try:
        # 这里可以实现更复杂的音频特征分析
        # 目前使用简单的启发式方法
        
        # 基于音频长度和特征的简单语言检测
        if len(audio_chunk) < 10000:  # 短音频
            return "en"  # 默认中文
        
        # 可以添加更多音频特征分析
        # 例如：频谱分析、音调特征、节奏模式等
        
        # 目前返回默认中文
        return "en"
        
    except Exception as e:
        logger.error(f"音频特征语言检测失败: {e}")
        return "en"

def detect_language_from_audio(audio_chunk: bytes) -> str:
    """从音频特征检测语言（公共接口）"""
    return _detect_language_from_audio_features(audio_chunk)

def get_supported_languages() -> Dict[str, Dict]:
    """获取支持的语言列表"""
    return SUPPORTED_LANGUAGES

def get_language_config(language_code: str) -> Optional[Dict]:
    """获取指定语言的配置"""
    return SUPPORTED_LANGUAGES.get(language_code)

def is_language_supported(language_code: str) -> bool:
    """检查是否支持指定语言"""
    return language_code in SUPPORTED_LANGUAGES 