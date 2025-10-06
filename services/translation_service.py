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
import json
import requests
from typing import Optional, Dict, Any
from loguru import logger

# 配置
from core.config import DEEPL_API_KEY, OPENAI_API_KEY, DEFAULT_TRANSLATE_TARGET_LANG, GOOGLE_APPLICATION_CREDENTIALS

# 语言代码映射
LANGUAGE_MAPPING = {
    "zh": "zh-CN",
    "en": "en",
    "ja": "ja",
    "ko": "ko",
    "fr": "fr",
    "de": "de",
    "es": "es",
    "ru": "ru",
    "ar": "ar",
    "hi": "hi"
}

def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """
    翻译文本
    Args:
        text: 要翻译的文本
        from_lang: 源语言代码
        to_lang: 目标语言代码
    Returns:
        翻译后的文本
    """
    try:
        # 如果源语言和目标语言相同，直接返回
        if from_lang == to_lang:
            return text
        
        # 尝试使用不同的翻译服务
        translated = _try_google_translate(text, from_lang, to_lang)
        if translated:
            return translated
        else:
            print("【API Service Failed!】google翻译失败!")
            
        translated = _try_deepl_translate(text, from_lang, to_lang)
        if translated:
            return translated
        else:
            print("【API Service Failed!】deepl翻译失败!")
            
        translated = _try_openai_translate(text, from_lang, to_lang)
        if translated:
            return translated
        else:
            print("【API Service Failed!】openai翻译失败!")
            
        # 使用备用翻译
        return _fallback_translation(text, from_lang, to_lang)
        
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        return text

def _try_google_translate(text: str, from_lang: str, to_lang: str) -> Optional[str]:
    """尝试使用Google Cloud Translation API"""
    try:
        from google.cloud import translate_v2 as translate
        
        client = translate.Client()
        
        # 准备翻译参数
        target = _get_google_language_code(to_lang)
        source = _get_google_language_code(from_lang)
        print(f"Google Translate: {text} -> {target} -> {source}")
        
        # 执行翻译
        result = client.translate(
            text,
            target_language=target,
            source_language=source
        )
        
        if result and 'translatedText' in result:
            return result['translatedText']
        
        return None
        
    except Exception as e:
        logger.warning(f"Google翻译失败: {e}")
        return None

def _try_deepl_translate(text: str, from_lang: str, to_lang: str) -> Optional[str]:
    """尝试使用DeepL API"""
    if not DEEPL_API_KEY:
        return None
    
    try:
        url = "https://api-free.deepl.com/v2/translate"
        headers = {
            "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "text": text,
            "source_lang": _get_deepl_language_code(from_lang),
            "target_lang": _get_deepl_language_code(to_lang)
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if "translations" in result and len(result["translations"]) > 0:
                return result["translations"][0]["text"]
        
        return None
        
    except Exception as e:
        logger.warning(f"DeepL翻译失败: {e}")
        return None

def _try_openai_translate(text: str, from_lang: str, to_lang: str) -> Optional[str]:
    """尝试使用OpenAI进行翻译"""
    if not OPENAI_API_KEY:
        return None
    
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        请将以下文本从{_get_language_name(from_lang)}翻译成{_get_language_name(to_lang)}：
        
        {text}
        
        请只返回翻译结果，不要其他内容。
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.warning(f"OpenAI翻译失败: {e}")
        return None

def _fallback_translation(text: str, from_lang: str, to_lang: str) -> str:
    """备用翻译（基于简单规则）"""
    # 这里可以实现一些简单的翻译规则
    # 目前返回原文本
    return text

def _get_google_language_code(lang: str) -> str:
    """获取Google Translate语言代码"""
    return LANGUAGE_MAPPING.get(lang, lang)

def _get_deepl_language_code(lang: str) -> str:
    """获取DeepL语言代码"""
    deepl_mapping = {
        "zh": "ZH",
        "en": "EN",
        "ja": "JA",
        "ko": "KO",
        "fr": "FR",
        "de": "DE",
        "es": "ES",
        "ru": "RU"
    }
    return deepl_mapping.get(lang, lang.upper())

def _get_language_name(lang: str) -> str:
    """获取语言名称"""
    language_names = {
        "zh": "中文",
        "en": "英文",
        "ja": "日文",
        "ko": "韩文",
        "fr": "法文",
        "de": "德文",
        "es": "西班牙文",
        "ru": "俄文",
        "ar": "阿拉伯文",
        "hi": "印地文"
    }
    return language_names.get(lang, lang)

def detect_language(text: str) -> str:
    """检测文本语言"""
    try:
        # 使用Google Cloud Translation API检测语言
        detected = _google_detect_language(text)
        if detected:
            return detected
        
        # 使用OpenAI检测语言
        if OPENAI_API_KEY:
            return _openai_detect_language(text)
        else:
            print("【API Service Failed!】openai语言检测失败!")
        
        # 使用简单规则检测
        return _rule_based_language_detection(text)
        
    except Exception as e:
        logger.error(f"语言检测失败: {e}")
        return 'zh'

def _google_detect_language(text: str) -> str:
    """使用Google Cloud Translation API检测语言"""
    try:
        from google.cloud import translate_v2 as translate
        
        client = translate.Client()
        result = client.detect_language(text)
        
        if result and hasattr(result, 'language'):
            detected_lang = result['language']
            # 转换为我们的语言代码格式
            for code, google_code in LANGUAGE_MAPPING.items():
                if google_code == detected_lang:
                    return code
            return detected_lang
        
        return "zh"
        
    except Exception as e:
        logger.warning(f"Google语言检测失败: {e}")
        return "zh"

def _openai_detect_language(text: str) -> str:
    """使用OpenAI检测语言"""
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        检测以下文本的语言，从以下选项中选择：
        - zh: 中文
        - en: 英文
        - ja: 日文
        - ko: 韩文
        - fr: 法文
        - de: 德文
        - es: 西班牙文
        - ru: 俄文
        
        文本: {text}
        
        请只返回语言代码，不要其他内容。
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        
        detected_lang = response.choices[0].message.content.strip()
        if detected_lang in ["zh", "en", "ja", "ko", "fr", "de", "es", "ru"]:
            return detected_lang
        
        return "zh"
        
    except Exception as e:
        logger.warning(f"OpenAI语言检测失败: {e}")
        return "zh"

def _rule_based_language_detection(text: str) -> str:
    """基于规则的语言检测"""
    # 简单的字符检测规则
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        return "zh"  # 包含中文字符
    elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
        return "ja"  # 包含日文字符
    elif any('\uac00' <= char <= '\ud7af' for char in text):
        return "ko"  # 包含韩文字符
    elif any('\u0600' <= char <= '\u06ff' for char in text):
        return "ar"  # 包含阿拉伯文字符
    elif any('\u0900' <= char <= '\u097f' for char in text):
        return "hi"  # 包含印地文字符
    else:
        return "en"  # 默认英文

def get_supported_languages() -> Dict[str, str]:
    """获取支持的语言列表"""
    return {
        "zh": "中文",
        "en": "English",
        "ja": "日本語",
        "ko": "한국어",
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español",
        "ru": "Русский",
        "ar": "العربية",
        "hi": "हिन्दी"
    }

def translate_batch(texts: list, from_lang: str, to_lang: str) -> list:
    """批量翻译"""
    results = []
    for text in texts:
        translated = translate_text(text, from_lang, to_lang)
        results.append(translated)
    return results 