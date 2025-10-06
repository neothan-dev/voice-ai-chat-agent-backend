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

from typing import Dict, Optional, List
from loguru import logger

# 多语言音色映射配置
MULTILINGUAL_VOICE_STYLES = {
    # 小晓音色 - 支持多种语言
    "xiaoxiao": {
        "name": "小晓",
        "description": "温柔甜美的女声",
        "voices": {
            "zh": "zh-CN-XiaoxiaoNeural",
            "en": "en-US-JennyNeural",
            "ja": "ja-JP-NanamiNeural",
            "ko": "ko-KR-SunHiNeural",
            "fr": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural",
            "es": "es-ES-ElviraNeural",
            "ru": "ru-RU-SvetlanaNeural",
            "ar": "ar-SA-ZariyahNeural",
            "hi": "hi-IN-SwaraNeural"
        },
        "fallback": "zh-CN-XiaoxiaoNeural"
    },
    
    # 云希音色 - 支持多种语言
    "yunxi": {
        "name": "云希",
        "description": "成熟稳重的男声",
        "voices": {
            "zh": "zh-CN-YunxiNeural",
            "en": "en-US-GuyNeural",
            "ja": "ja-JP-KeitaNeural",
            "ko": "ko-KR-InJoonNeural",
            "fr": "fr-FR-HenriNeural",
            "de": "de-DE-ConradNeural",
            "es": "es-ES-AlvaroNeural",
            "ru": "ru-RU-DmitryNeural",
            "ar": "ar-SA-HamedNeural",
            "hi": "hi-IN-MadhurNeural"
        },
        "fallback": "zh-CN-YunxiNeural"
    },
    
    # 云扬音色 - 支持多种语言
    "yunyang": {
        "name": "云扬",
        "description": "专业播报的男声",
        "voices": {
            "zh": "zh-CN-YunyangNeural",
            "en": "en-US-AriaNeural",
            "ja": "ja-JP-NaokiNeural",
            "ko": "ko-KR-YuJinNeural",
            "fr": "fr-FR-AlainNeural",
            "de": "de-DE-AmalaNeural",
            "es": "es-ES-LaiaNeural",
            "ru": "ru-RU-DariyaNeural",
            "ar": "ar-SA-SalimNeural",
            "hi": "hi-IN-AarohiNeural"
        },
        "fallback": "zh-CN-YunyangNeural"
    },
    
    # 小艺音色 - 支持多种语言
    "xiaoyi": {
        "name": "小艺",
        "description": "活泼可爱的女声",
        "voices": {
            "zh": "zh-CN-XiaoyiNeural",
            "en": "en-US-JennyNeural",
            "ja": "ja-JP-NanamiNeural",
            "ko": "ko-KR-SunHiNeural",
            "fr": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural",
            "es": "es-ES-ElviraNeural",
            "ru": "ru-RU-SvetlanaNeural",
            "ar": "ar-SA-ZariyahNeural",
            "hi": "hi-IN-SwaraNeural"
        },
        "fallback": "zh-CN-XiaoyiNeural"
    },
    
    # 默认音色 - 支持多种语言
    "default": {
        "name": "默认",
        "description": "标准AI助手音色",
        "voices": {
            "zh": "zh-CN-XiaoxiaoNeural",
            "en": "en-US-JennyNeural",
            "ja": "ja-JP-NanamiNeural",
            "ko": "ko-KR-SunHiNeural",
            "fr": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural",
            "es": "es-ES-ElviraNeural",
            "ru": "ru-RU-SvetlanaNeural",
            "ar": "ar-SA-ZariyahNeural",
            "hi": "hi-IN-SwaraNeural"
        },
        "fallback": "zh-CN-XiaoxiaoNeural"
    }
}

def get_voice_for_language_and_style(voice_style: str, language: str) -> str:
    """
    根据音色风格和语言获取对应的语音
    Args:
        voice_style: 音色风格（xiaoxiao, yunxi, yunyang, xiaoyi, default）
        language: 语言代码
    Returns:
        对应的Azure语音名称
    """
    try:
        # 获取音色配置
        style_config = MULTILINGUAL_VOICE_STYLES.get(voice_style, MULTILINGUAL_VOICE_STYLES["default"])
        
        # 获取对应语言的语音
        voice = style_config["voices"].get(language, style_config["fallback"])
        
        logger.info(f"音色 {voice_style} 语言 {language} -> 语音 {voice}")
        return voice
        
    except Exception as e:
        logger.error(f"获取音色语音失败: {e}")
        return MULTILINGUAL_VOICE_STYLES["default"]["fallback"]

def get_available_voice_styles() -> List[Dict]:
    """
    获取可用的音色风格列表
    Returns:
        音色风格列表
    """
    styles = []
    for style_id, config in MULTILINGUAL_VOICE_STYLES.items():
        styles.append({
            "id": style_id,
            "name": config["name"],
            "description": config["description"],
            "supported_languages": list(config["voices"].keys())
        })
    return styles

def get_voice_style_info(voice_style: str) -> Optional[Dict]:
    """
    获取音色风格信息
    Args:
        voice_style: 音色风格ID
    Returns:
        音色风格信息
    """
    if voice_style in MULTILINGUAL_VOICE_STYLES:
        config = MULTILINGUAL_VOICE_STYLES[voice_style]
        return {
            "id": voice_style,
            "name": config["name"],
            "description": config["description"],
            "supported_languages": list(config["voices"].keys()),
            "voices": config["voices"]
        }
    return None

def is_voice_style_supported(voice_style: str) -> bool:
    """
    检查音色风格是否支持
    Args:
        voice_style: 音色风格ID
    Returns:
        是否支持
    """
    return voice_style in MULTILINGUAL_VOICE_STYLES

def get_supported_languages_for_style(voice_style: str) -> List[str]:
    """
    获取音色风格支持的语言列表
    Args:
        voice_style: 音色风格ID
    Returns:
        支持的语言列表
    """
    if voice_style in MULTILINGUAL_VOICE_STYLES:
        return list(MULTILINGUAL_VOICE_STYLES[voice_style]["voices"].keys())
    return []

def validate_voice_style_and_language(voice_style: str, language: str) -> bool:
    """
    验证音色风格和语言是否匹配
    Args:
        voice_style: 音色风格ID
        language: 语言代码
    Returns:
        是否匹配
    """
    if voice_style not in MULTILINGUAL_VOICE_STYLES:
        return False
    
    supported_languages = MULTILINGUAL_VOICE_STYLES[voice_style]["voices"].keys()
    return language in supported_languages

def get_fallback_voice(voice_style: str) -> str:
    """
    获取音色风格的备用语音
    Args:
        voice_style: 音色风格ID
    Returns:
        备用语音名称
    """
    if voice_style in MULTILINGUAL_VOICE_STYLES:
        return MULTILINGUAL_VOICE_STYLES[voice_style]["fallback"]
    return MULTILINGUAL_VOICE_STYLES["default"]["fallback"]

def update_emotion_voice_params_for_style(voice_style: str, language: str):
    """
    更新情感语音参数以使用指定音色和语言
    Args:
        voice_style: 音色风格ID
        language: 语言代码
    Returns:
        更新后的语音参数
    """
    try:
        from services.tts_service import EMOTION_VOICE_PARAMS
        
        # 获取对应语言的语音
        voice = get_voice_for_language_and_style(voice_style, language)
        
        # 更新所有情感的语音参数
        updated_params = {}
        for emotion, params in EMOTION_VOICE_PARAMS.items():
            updated_params[emotion] = params.copy()
            updated_params[emotion]['azure_voice'] = voice
        
        logger.info(f"更新音色参数: {voice_style} + {language} -> {voice}")
        return updated_params
        
    except Exception as e:
        logger.error(f"更新音色参数失败: {e}")
        return EMOTION_VOICE_PARAMS

def get_voice_style_preview(voice_style: str, language: str) -> Dict:
    """
    获取音色风格预览信息
    Args:
        voice_style: 音色风格ID
        language: 语言代码
    Returns:
        预览信息
    """
    try:
        voice = get_voice_for_language_and_style(voice_style, language)
        style_info = get_voice_style_info(voice_style)
        
        return {
            "voice_style": voice_style,
            "language": language,
            "voice": voice,
            "style_name": style_info["name"] if style_info else "未知",
            "description": style_info["description"] if style_info else "",
            "is_supported": validate_voice_style_and_language(voice_style, language)
        }
        
    except Exception as e:
        logger.error(f"获取音色预览失败: {e}")
        return {
            "voice_style": voice_style,
            "language": language,
            "voice": get_fallback_voice(voice_style),
            "style_name": "默认",
            "description": "默认音色",
            "is_supported": False
        }

def validate_voice_style_id(voice_style: str) -> bool:
    """
    验证音色ID是否有效
    Args:
        voice_style: 音色ID
    Returns:
        是否有效
    """
    return voice_style in MULTILINGUAL_VOICE_STYLES

def get_voice_style_name(voice_style: str) -> str:
    """
    根据音色ID获取音色名称
    Args:
        voice_style: 音色ID
    Returns:
        音色名称
    """
    if voice_style in MULTILINGUAL_VOICE_STYLES:
        return MULTILINGUAL_VOICE_STYLES[voice_style]["name"]
    return "未知音色"

def get_voice_style_description(voice_style: str) -> str:
    """
    根据音色ID获取音色描述
    Args:
        voice_style: 音色ID
    Returns:
        音色描述
    """
    if voice_style in MULTILINGUAL_VOICE_STYLES:
        return MULTILINGUAL_VOICE_STYLES[voice_style]["description"]
    return "未知音色描述"
