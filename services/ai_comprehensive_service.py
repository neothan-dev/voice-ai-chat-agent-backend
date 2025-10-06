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

from services.stt_service import stt_stream
from services.nlp_service import get_ai_response
from services.emotion_service import analyze_emotion
from services.tts_service import tts_stream
from services.explain_service import explain_response
from services.log_service import log_interaction
from services.navigation_service import navigation_service
from services.translation_service import translate_text, detect_language, get_supported_languages
import io
import wave
import re
from typing import Dict, List, Tuple, Optional, AsyncGenerator
from loguru import logger

# 导入通用配置管理器
from utils.config_manager import CONFIG_LOADER

# 支持的语言配置
SUPPORTED_LANGUAGES = {
    "zh": {"name": "中文", "locale": "zh-CN", "fallback": "zh"},
    "en": {"name": "English", "locale": "en-US", "fallback": "en"},
    "ja": {"name": "日本語", "locale": "ja-JP", "fallback": "ja"},
    "ko": {"name": "한국어", "locale": "ko-KR", "fallback": "ko"},
    "fr": {"name": "Français", "locale": "fr-FR", "fallback": "fr"},
    "de": {"name": "Deutsch", "locale": "de-DE", "fallback": "de"},
    "es": {"name": "Español", "locale": "es-ES", "fallback": "es"},
    "ru": {"name": "Русский", "locale": "ru-RU", "fallback": "ru"},
    "ar": {"name": "العربية", "locale": "ar-SA", "fallback": "ar"},
    "hi": {"name": "हिन्दी", "locale": "hi-IN", "fallback": "hi"}
}

# 多语言回复模板
MULTILINGUAL_RESPONSES = {
    "greeting": {
        "zh": "你好！我是你的健康AI助手，很高兴为您服务。",
        "en": "Hello! I'm your health AI assistant, glad to serve you.",
        "ja": "こんにちは！私はあなたの健康AIアシスタントです。お手伝いできることを嬉しく思います。",
        "ko": "안녕하세요! 저는 당신의 건강 AI 어시스턴트입니다. 도움을 드릴 수 있어서 기쁩니다.",
        "fr": "Bonjour ! Je suis votre assistant IA de santé, ravi de vous servir.",
        "de": "Hallo! Ich bin Ihr Gesundheits-KI-Assistent, freue mich, Ihnen zu helfen.",
        "es": "¡Hola! Soy tu asistente de IA de salud, me alegra ayudarte.",
        "ru": "Привет! Я ваш ИИ-помощник по здоровью, рад помочь вам.",
        "ar": "مرحباً! أنا مساعد الذكاء الاصطناعي الصحي الخاص بك، يسعدني خدمتك.",
        "hi": "नमस्ते! मैं आपका स्वास्थ्य AI सहायक हूं, आपकी सेवा करके खुशी हो रही है।"
    },
    "health_advice": {
        "zh": "根据您的描述，我建议您注意以下几点：",
        "en": "Based on your description, I suggest you pay attention to the following:",
        "ja": "あなたの説明に基づいて、以下の点に注意することをお勧めします：",
        "ko": "귀하의 설명에 따라 다음 사항에 주의하시기 바랍니다:",
        "fr": "Selon votre description, je vous suggère de prêter attention aux points suivants :",
        "de": "Basierend auf Ihrer Beschreibung schlage ich vor, dass Sie auf Folgendes achten:",
        "es": "Según su descripción, le sugiero que preste atención a lo siguiente:",
        "ru": "Основываясь на вашем описании, я предлагаю обратить внимание на следующее:",
        "ar": "بناءً على وصفك، أقترح عليك الانتباه إلى النقاط التالية:",
        "hi": "आपके विवरण के आधार पर, मैं सुझाव देता हूं कि आप निम्नलिखित बातों पर ध्यान दें:"
    },
    "error": {
        "zh": "抱歉，我暂时无法理解您的请求。请重新表述或尝试其他问题。",
        "en": "Sorry, I cannot understand your request at the moment. Please rephrase or try another question.",
        "ja": "申し訳ございませんが、現在お客様のリクエストを理解できません。言い換えるか、別の質問を試してください。",
        "ko": "죄송합니다. 현재 귀하의 요청을 이해할 수 없습니다. 다시 표현하거나 다른 질문을 시도해 주세요.",
        "fr": "Désolé, je ne peux pas comprendre votre demande pour le moment. Veuillez reformuler ou essayer une autre question.",
        "de": "Entschuldigung, ich kann Ihre Anfrage derzeit nicht verstehen. Bitte formulieren Sie es anders oder versuchen Sie eine andere Frage.",
        "es": "Lo siento, no puedo entender su solicitud en este momento. Por favor reformule o intente otra pregunta.",
        "ru": "Извините, я не могу понять ваш запрос в данный момент. Пожалуйста, переформулируйте или попробуйте другой вопрос.",
        "ar": "عذراً، لا أستطيع فهم طلبك في الوقت الحالي. يرجى إعادة الصياغة أو تجربة سؤال آخر.",
        "hi": "क्षमा करें, मैं वर्तमान में आपके अनुरोध को समझ नहीं सकता। कृपया पुनः व्यक्त करें या कोई अन्य प्रश्न आज़माएं।"
    }
}

def split_text_into_sentences(text: str, lang: str = "zh") -> List[str]:
    """
    将文本按句子分割（支持多语言）
    Args:
        text: 要分割的文本
        lang: 语言代码
    Returns:
        句子列表
    """
    # 多语言句子分割规则
    sentence_patterns = {
        "zh": r'[。！？；]',  # 中文：句号、感叹号、问号、分号
        "ja": r'[。！？；]',  # 日语：句号、感叹号、问号、分号
        "ko": r'[.!?;]',     # 韩语：句号、感叹号、问号、分号
        "ar": r'[.!?;؟]',    # 阿拉伯语：句号、感叹号、问号、分号、阿拉伯问号
        "default": r'[.!?;]'  # 其他语言：句号、感叹号、问号、分号
    }
    
    pattern = sentence_patterns.get(lang, sentence_patterns["default"])
    sentences = re.split(pattern, text)
    
    # 过滤空字符串并清理
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def detect_user_language_preference(text: str, detected_lang: str, session_history: Optional[Dict] = None) -> str:
    """
    检测用户语言偏好（动态检测版）
    Args:
        text: 用户输入文本
        detected_lang: 检测到的语言
        session_history: 会话历史
    Returns:
        用户偏好的语言代码
    """
    # 1. 优先使用STT检测到的语言（最准确）
    if detected_lang and detected_lang in SUPPORTED_LANGUAGES:
        print(f"使用STT检测到的语言: {detected_lang}")
        return detected_lang
    
    # 2. 基于文本内容进行语言检测
    try:
        fallback_lang = detect_language(text)
        if fallback_lang in SUPPORTED_LANGUAGES:
            print(f"基于文本内容检测到语言: {fallback_lang}")
            return fallback_lang
    except Exception as e:
        logger.warning(f"语言检测失败: {e}")
    
    # 3. 基于文本特征进行启发式语言检测
    heuristic_lang = _detect_language_heuristic(text)
    if heuristic_lang in SUPPORTED_LANGUAGES:
        print(f"启发式检测到语言: {heuristic_lang}")
        return heuristic_lang
    
    # 4. 如果有会话历史，使用历史语言偏好作为备用
    if session_history:
        for field in ["preferred_language", "user_language", "language", "lang"]:
            if field in session_history and session_history[field]:
                preferred_lang = session_history[field]
                if preferred_lang in SUPPORTED_LANGUAGES:
                    print(f"使用会话历史语言偏好: {preferred_lang}")
                    return preferred_lang
    
    # 5. 默认返回中文
    print("使用默认语言: en")
    return "en"

def _detect_language_heuristic(text: str) -> str:
    """
    基于文本特征的启发式语言检测
    """
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

def get_localized_response(response_type: str, lang: str, **kwargs) -> str:
    """
    获取本地化回复
    Args:
        response_type: 回复类型
        lang: 语言代码
        **kwargs: 额外参数
    Returns:
        本地化回复文本
    """
    # 获取语言配置
    lang_config = SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES["en"])
    
    # 获取本地化回复模板
    if response_type in MULTILINGUAL_RESPONSES:
        response = MULTILINGUAL_RESPONSES[response_type].get(lang)
        if response:
            return response
    
    # 如果没有找到本地化回复，使用英文作为备用
    fallback_response = MULTILINGUAL_RESPONSES[response_type].get("en", "I'm sorry, I cannot process your request.")
    
    # 如果用户语言不是英文，尝试翻译
    if lang != "en":
        try:
            return translate_text(fallback_response, "en", lang)
        except:
            return fallback_response
    
    return fallback_response

def enhance_multilingual_nlp(text: str, lang: str, session_id: str, user_id: str, current_page: Optional[Dict] = None) -> Tuple[str, int, float]:
    """
    增强的多语言NLP处理
    Args:
        text: 用户输入文本
        lang: 语言代码
        session_id: 会话ID
        user_id: 用户ID
        current_page: 当前页面信息（包含路由等）
    Returns:
        (reply, intent_id, confidence): AI回复、意图ID、置信度
    """
    try:
        # 打印当前页面信息
        if current_page:
            print(f"当前页面信息: {current_page}")
            current_route = current_page.get('route', 'unknown')
            print(f"当前路由: {current_route}")
        else:
            print(f"未提供当前页面信息: {current_page}")
        
        # 1. 多语言意图识别（考虑当前页面上下文）
        intent_id, confidence = _multilingual_intent_detection(text, lang, current_page)
        
        # 2. 生成多语言回复（考虑当前页面上下文）
        reply = _generate_multilingual_reply(intent_id, text, lang, session_id, user_id, current_page)
        
        return reply, intent_id, confidence
        
    except Exception as e:
        logger.error(f"多语言NLP处理失败: {e}")
        print(f"多语言NLP处理失败: {e}")
        return get_localized_response("error", lang), 100001, 0.5

def _multilingual_intent_detection(text: str, lang: str, current_page: Optional[Dict] = None) -> Tuple[int, float]:
    """
    多语言意图识别（考虑当前页面上下文）
    """
    try:
        # 使用OpenAI进行多语言意图识别
        from services.nlp_service import _openai_intent_detection
        intent_id, confidence = _openai_intent_detection(text, lang)
        if intent_id:
            return intent_id, confidence
        
        # 使用关键词匹配（支持多语言，考虑页面上下文）
        return _multilingual_keyword_detection(text, lang, current_page)
        
    except Exception as e:
        logger.error(f"多语言意图识别失败: {e}")
        print(f"多语言意图识别失败: {e}")
        return 100001, 0.5

def _multilingual_keyword_detection(text: str, lang: str, current_page: Optional[Dict] = None) -> Tuple[int, float]:
    """
    多语言关键词检测（考虑当前页面上下文）
    """
    # 多语言关键词映射
    multilingual_keywords = {
        "greeting": {
            "zh": ["你好", "您好", "早上好", "下午好", "晚上好", "嗨"],
            "en": ["hello", "hi", "good morning", "good afternoon", "good evening", "hey"],
            "ja": ["こんにちは", "おはよう", "こんばんは", "はじめまして"],
            "ko": ["안녕하세요", "안녕", "좋은 아침", "좋은 저녁"],
            "fr": ["bonjour", "salut", "bonsoir", "coucou"],
            "de": ["hallo", "guten tag", "guten morgen", "guten abend"],
            "es": ["hola", "buenos días", "buenas tardes", "buenas noches"],
            "ru": ["привет", "здравствуйте", "доброе утро", "добрый вечер"],
            "ar": ["مرحبا", "أهلا", "صباح الخير", "مساء الخير"],
            "hi": ["नमस्ते", "हैलो", "सुप्रभात", "शुभ संध्या"]
        },
        "health_question": {
            "zh": ["健康", "身体", "症状", "疾病", "治疗", "医生", "医院"],
            "en": ["health", "body", "symptom", "disease", "treatment", "doctor", "hospital"],
            "ja": ["健康", "体", "症状", "病気", "治療", "医者", "病院"],
            "ko": ["건강", "몸", "증상", "질병", "치료", "의사", "병원"],
            "fr": ["santé", "corps", "symptôme", "maladie", "traitement", "médecin", "hôpital"],
            "de": ["gesundheit", "körper", "symptom", "krankheit", "behandlung", "arzt", "krankenhaus"],
            "es": ["salud", "cuerpo", "síntoma", "enfermedad", "tratamiento", "médico", "hospital"],
            "ru": ["здоровье", "тело", "симптом", "болезнь", "лечение", "врач", "больница"],
            "ar": ["صحة", "جسم", "عرض", "مرض", "علاج", "طبيب", "مستشفى"],
            "hi": ["स्वास्थ्य", "शरीर", "लक्षण", "बीमारी", "उपचार", "डॉक्टर", "अस्पताल"]
        }
    }
    
    text_lower = text.lower()
    
    # 如果有当前页面信息，可以根据页面类型调整意图识别
    if current_page:
        current_route = current_page.get('route', '')
        print(f"当前页面路由: {current_route}")
        
        # 根据当前页面调整意图识别逻辑
        if 'voice_chat' in current_route:
            print("用户在语音聊天页面，增强语音相关意图识别")
        elif 'dashboard' in current_route:
            print("用户在仪表板页面，增强导航相关意图识别")
        elif 'health' in current_route:
            print("用户在健康相关页面，增强健康问题意图识别")
    
    # 检查每种意图的关键词
    for intent_name, lang_keywords in multilingual_keywords.items():
        if lang in lang_keywords:
            for keyword in lang_keywords[lang]:
                if keyword in text_lower:
                    # 根据意图名称返回对应的意图ID
                    if intent_name == "greeting":
                        return 100002, 0.8  # 问候意图ID
                    elif intent_name == "health_question":
                        return 100003, 0.8  # 健康问题意图ID
    
    return 100001, 0.5  # 默认通用意图

def _generate_multilingual_reply(intent_id: int, user_input: str, lang: str, session_id: str, user_id: str, current_page: Optional[Dict] = None) -> str:
    """
    生成多语言回复（增强版，考虑当前页面上下文）
    """
    try:
        # 获取意图配置
        intent_config = CONFIG_LOADER.get_config_value("nlp", "Intent", intent_id)
        if not intent_config:
            return get_localized_response("error", lang)
        
        # 如果有当前页面信息，可以根据页面上下文调整回复
        if current_page:
            current_route = current_page.get('route', '')
            print(f"生成回复时考虑当前页面: {current_route}")
            
            # 根据当前页面调整回复内容
            if 'voice_chat' in current_route:
                print("在语音聊天页面，提供语音相关帮助")
            elif 'dashboard' in current_route:
                print("在仪表板页面，提供导航相关帮助")
            elif 'health' in current_route:
                print("在健康页面，提供健康相关建议")
        
        # 使用默认的NLP服务生成回复
        from services.nlp_service import generate_reply
        reply = generate_reply(intent_id, user_input, lang, session_id, user_id, current_page)

        return reply
        
    except Exception as e:
        logger.error(f"多语言回复生成失败: {e}")
        return get_localized_response("error", lang)

# def ai_comprehensive_service(audio_chunk: bytes, session_id: str, user_id: str, voice_style: str = None, explain_flag: bool = False, session_history: Optional[Dict] = None):
#     """
#     多语言AI综合服务（支持会话管理）
#     Args:
#         audio_chunk: 音频数据
#         session_id: 会话ID
#         user_id: 用户ID
#         voice_style: 语音风格
#         explain_flag: 是否启用解释
#         session_history: 会话历史（包含语言偏好等信息）
#     Returns:
#         音频段、意图描述、置信度、情感、解释、导航结果
#     """
#     # 处理整句音频
#     # stt, nlp, tts, send back
    
#     # 检查是否有WAV头
#     def has_wav_header(b):
#         return b[:4] == b'RIFF' and b[8:12] == b'WAVE'
    
#     if not has_wav_header(audio_chunk):
#         print("[AI] 自动补充WAV头")
#         # 假设采样率16000, 单声道, 16bit
#         sample_rate = 16000
#         num_channels = 1
#         sample_width = 2
#         wav_buf = io.BytesIO()
#         with wave.open(wav_buf, 'wb') as wf:
#             wf.setnchannels(num_channels)
#             wf.setsampwidth(sample_width)
#             wf.setframerate(sample_rate)
#             wf.writeframes(audio_chunk)
#         audio_chunk = wav_buf.getvalue()
    
#     # 1. 会话管理初始化
#     print("\n#[BEGIN] -> session_management")
#     from services.session_service import session_manager
    
#     # 获取或创建会话（不设置默认语言）
#     actual_session_id = session_manager.get_or_create_session(
#         user_id=int(user_id),
#         session_id=session_id if session_id != "None" else None,
#         voice_style=voice_style
#     )
    
#     # 获取会话信息
#     session_info = session_manager.get_session(actual_session_id)
#     if session_info:
#         print(f"使用会话: {actual_session_id} (用户: {user_id}, 当前语言: {session_info.language or '未检测'})")
#     print("##[END] session_management")
    
#     # 2. 语音转文本（完全动态语言检测）
#     print("\n#[BEGIN] -> stt_stream")
    
#     # 不传递preferred_language，让STT完全自主检测
#     text, detected_lang, _method = stt_stream(audio_chunk)
#     print('*************************************************************************************')
#     print("stt text ->", text, "detected_lang ->", detected_lang)
#     print('*************************************************************************************')
#     print("##[END] stt method ->", _method)
    
#     # 2. 动态语言检测和会话语言更新
#     user_lang = detect_user_language_preference(text, detected_lang, session_history)
#     print(f"检测到语言: {user_lang} (STT检测: {detected_lang})")
    
#     # 更新会话的主要语言（基于语言分布统计）
#     if session_info:
#         session_manager.update_session_language(actual_session_id, user_lang)
#         print(f"会话语言已更新: {user_lang}")
    
#     # 3. 导航意图检测（多语言）
#     print("\n#[BEGIN] -> navigation_detection")
#     navigation_result, _method = navigation_service.detect_navigation_intent(text, user_lang)
#     print("navigation ->", navigation_result)
#     print("##[END] navigation_detection method ->", _method)
    
#     # 4. 多语言NLP对话+情感分析（支持会话上下文）
#     print("\n#[BEGIN] -> enhance_multilingual_nlp")
#     reply, intent_id, confidence = enhance_multilingual_nlp(text, user_lang, actual_session_id, user_id)
#     intent_desc = CONFIG_LOADER.get_config_value("nlp", "Intent", intent_id)
#     intent_desc_text = intent_desc.get('Description', '') if intent_desc else ''
#     print("nlp! ->", intent_id, confidence, reply)
#     print("##[END] enhance_multilingual_nlp")
    
#     print("\n#[BEGIN] -> analyze_emotion")
#     emotion, _method = analyze_emotion(text, user_lang)
#     print("emo ->", emotion)
#     print("##[END] emo method ->", _method)
    
#     # 5. 解释（多语言）
#     explain, _method = None, None
#     if explain_flag:
#         print("\n#[BEGIN] -> explain_response")
#         explain, _method = explain_response(text, reply, intent_desc_text, emotion, user_lang)
#         print("explain ->", explain)
#         print("##[END] explain method ->", _method)
    
#     # 6. 字幕分段处理（多语言）
#     print("\n#[BEGIN] -> subtitle_segmentation")
#     sentences = split_text_into_sentences(reply, user_lang)
#     print("sentences ->", sentences)
#     print("##[END] subtitle_segmentation")
    
#     # 7. 为每个句子生成音频（支持多语言和情感）
#     print("\n#[BEGIN] -> tts_stream_segments")
#     audio_segments = []
    
#     # 如果指定了音色，使用多语言音色服务
#     if voice_style:
#         print(f"使用音色: {voice_style} 语言: {user_lang}")
#         # 音色参数会在tts_stream函数内部根据语言自动选择对应的语音
    
#     try:
#         for sentence in sentences:
#             # 传递音色参数到TTS服务
#             ai_audio, _method = tts_stream(sentence, user_lang, emotion, voice_style)
#             audio_segments.append({
#                 'text': sentence,
#                 'audio': ai_audio,
#                 'method': _method,
#                 'emotion': emotion,
#                 'language': user_lang,
#                 'voice_style': voice_style
#             })
#     except Exception as e:
#         logger.error(f"TTS生成失败: {e}")
#         # 如果失败，使用默认音色重试
#         for sentence in sentences:
#             ai_audio, _method = tts_stream(sentence, user_lang, emotion)
#             audio_segments.append({
#                 'text': sentence,
#                 'audio': ai_audio,
#                 'method': _method,
#                 'emotion': emotion,
#                 'language': user_lang,
#                 'voice_style': 'default'
#             })
    
#     print("##[END] tts_stream_segments")
    
#     # 8. 会话消息记录
#     print("\n#[BEGIN] -> session_message_logging")
#     if session_info:
#         # 记录用户消息
#         session_manager.add_message(
#             session_id=actual_session_id,
#             message_type="user",
#             content=text,
#             language=user_lang,
#             emotion=emotion
#         )
        
#         # 记录AI回复
#         session_manager.add_message(
#             session_id=actual_session_id,
#             message_type="ai",
#             content=reply,
#             intent_id=intent_id,
#             confidence=confidence,
#             emotion=emotion,
#             language=user_lang,
#             metadata={
#                 "voice_style": voice_style,
#                 "explain": explain,
#                 "navigation": navigation_result
#             }
#         )
        
#         # 更新上下文摘要
#         session_manager.update_context_summary(actual_session_id)
    
#     print("##[END] session_message_logging")
    
#     # 9. 日志与持久化（包含语言信息）
#     print("\n#[BEGIN] -> log_interaction")
#     log_interaction(actual_session_id, user_id, text, reply, emotion, intent_id, confidence, explain, user_lang)
#     print("##[END] log_interaction")

#     return audio_segments, intent_desc_text, confidence, emotion, explain, navigation_result, user_lang


async def ai_comprehensive_service_stream(
    audio_data: bytes,
    session_id: str,
    user_id: int,
    voice_style: Optional[str] = None,
    current_page: Optional[Dict] = None,
    explain_flag: bool = False
) -> AsyncGenerator[Dict, None]:
    """
    多语言AI综合服务 - 流式版本，每段音频生成后立即返回
    Args:
        audio_data: 音频数据
        session_id: 会话ID
        user_id: 用户ID
        voice_style: 音色选择
        explain_flag: 是否生成解释
        current_page: 当前页面信息（包含路由等）
    Yields:
        包含音频段信息的字典
    """
    print("\n#[BEGIN] -> ai_comprehensive_service_stream")
    
    # 检查是否有WAV头
    def has_wav_header(b):
        return b[:4] == b'RIFF' and b[8:12] == b'WAVE'
    
    if not has_wav_header(audio_data):
        print("[AI] 自动补充WAV头")
        # 假设采样率16000, 单声道, 16bit
        sample_rate = 16000
        num_channels = 1
        sample_width = 2
        wav_buf = io.BytesIO()
        with wave.open(wav_buf, 'wb') as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data)
        audio_data = wav_buf.getvalue()
    
    # 1. 会话管理初始化
    print("\n#[BEGIN] -> session_management")
    from services.session_service import session_manager
    
    # 获取或创建会话（不设置默认语言）
    actual_session_id = session_manager.get_or_create_session(
        user_id=user_id,
        session_id=session_id if session_id != "None" else None,
        voice_style=voice_style
    )
    
    # 获取会话信息
    session_info = session_manager.get_session(actual_session_id)
    if session_info:
        print(f"使用会话: {actual_session_id} (用户: {user_id}, 当前语言: {session_info.language or '未检测'})")
    print("##[END] session_management")
    
    # 2. 语音转文字（多语言）
    print("\n#[BEGIN] -> stt_stream")
    succ, text, detected_lang, _method = stt_stream(audio_data)
    print('*************************************************************************************')
    print("stt ->", text, "flags -> ", succ, detected_lang)
    print('*************************************************************************************')
    print("##[END] stt method ->", _method)

    # 3. 动态语言检测和会话语言更新
    # user_lang = detect_user_language_preference(text, detected_lang, None)
    # print(f"检测到语言: {user_lang} (STT检测: {detected_lang})")
    user_lang = detected_lang

    # 更新会话的主要语言（基于语言分布统计）
    if session_info:
        session_manager.update_session_language(actual_session_id, user_lang)
        print(f"会话语言已更新: {user_lang}")

    if succ:
        # 4. 导航服务（多语言）
        print("\n#[BEGIN] -> navigation_service")
        navigation_result, _method = navigation_service.detect_navigation_intent(text, user_lang)
        if navigation_result.get('route') == current_page.get('route'):
            navigation_result = {
                "type": "none",
                "action": None,
                "confidence": 0.0,
                "message": "已在当前页面"
            }
        print("nav ->", navigation_result)
        print("##[END] navigation")
        
        # 5. 情感分析（多语言）
        print("\n#[BEGIN] -> analyze_emotion")
        emotion, _method = analyze_emotion(text, user_lang)
        print("emo ->", emotion)
        print("##[END] emo method ->", _method)
        
        # 6. NLP处理（多语言）
        print("\n#[BEGIN] -> enhance_multilingual_nlp")
        reply, intent_id, confidence = enhance_multilingual_nlp(text, user_lang, actual_session_id, user_id, current_page)
        intent_desc = CONFIG_LOADER.get_config_value("nlp", "Intent", intent_id)
        intent_desc_text = intent_desc.get('Description', '') if intent_desc else ''
        print("nlp! ->", intent_id, confidence, reply)
        print("##[END] enhance_multilingual_nlp")
        
        # 7. 解释（多语言）
        # explain, _method = None, None
        # if explain_flag:
        #     print("\n#[BEGIN] -> explain_response")
        #     explain, _method = explain_response(text, reply, intent_desc_text, emotion, user_lang)
        #     print("explain ->", explain)
        #     print("##[END] explain method ->", _method)
        explain = ''
    
    else:
        reply = text
        emotion = '中性'
        confidence = 0.1
        intent_id = 100001
        intent_desc_text = ''
        explain = ''
        navigation_result = {
                        "type": "none",
                        "action": None,
                        "confidence": 0.0,
                        "message": "未识别到导航意图"
                    }

    
    # 8. 字幕分段处理（多语言）
    print("\n#[BEGIN] -> subtitle_segmentation")
    sentences = split_text_into_sentences(reply, user_lang)
    print("sentences ->", sentences)
    print("##[END] subtitle_segmentation")
    
    # 9. 为每个句子生成音频（支持多语言和情感）- 流式处理
    print("\n#[BEGIN] -> tts_stream_segments")
    
    # 如果指定了音色，使用多语言音色服务
    if voice_style:
        print(f"使用音色: {voice_style} 语言: {user_lang}")
        # 音色参数会在tts_stream函数内部根据语言自动选择对应的语音
    
    try:
        for i, sentence in enumerate(sentences):
            # 传递音色参数到TTS服务
            ai_audio, _method = tts_stream(sentence, user_lang, emotion, voice_style)
            
            # 立即返回当前音频段
            segment_data = {
                'type': 'audio_segment',
                'index': i,
                'total': len(sentences),
                'text': sentence,
                'audio': ai_audio,
                'method': _method,
                'emotion': emotion,
                'language': user_lang,
                'voice_style': voice_style
            }
            yield segment_data
            
    except Exception as e:
        logger.error(f"TTS生成失败: {e}")
        # 如果失败，使用默认音色重试
        for i, sentence in enumerate(sentences):
            ai_audio, _method = tts_stream(sentence, user_lang, emotion)
            
            # 立即返回当前音频段
            segment_data = {
                'type': 'audio_segment',
                'index': i,
                'total': len(sentences),
                'text': sentence,
                'audio': ai_audio,
                'method': _method,
                'emotion': emotion,
                'language': user_lang,
                'voice_style': 'default'
            }
            yield segment_data
    
    print("##[END] tts_stream_segments")
    
    # 10. 会话消息记录
    print("\n#[BEGIN] -> session_message_logging")
    if session_info:
        # 记录用户消息
        session_manager.add_message(
            session_id=actual_session_id,
            message_type="user",
            content=text,
            language=user_lang,
            emotion=emotion
        )
        
        # 记录AI回复
        session_manager.add_message(
            session_id=actual_session_id,
            message_type="ai",
            content=reply,
            intent_id=intent_id,
            confidence=confidence,
            emotion=emotion,
            language=user_lang,
            metadata={
                "voice_style": voice_style,
                "explain": explain,
                "navigation": navigation_result
            }
        )
        
        # 更新上下文摘要
        session_manager.update_context_summary(actual_session_id)
    
    print("##[END] session_message_logging")
    
    # 11. 日志与持久化（包含语言信息）
    print("\n#[BEGIN] -> log_interaction")
    log_interaction(actual_session_id, user_id, text, reply, emotion, intent_id, confidence, explain, user_lang)
    print("##[END] log_interaction")

    # 12. 返回最终结果
    final_result = {
        'type': 'final_result',
        'intent': intent_desc_text,
        'confidence': confidence,
        'emotion': emotion,
        'explain': explain,
        'navigation': navigation_result,
        'user_lang': user_lang
    }
    yield final_result
    
    print("##[END] ai_comprehensive_service_stream")