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

from typing import Tuple
import os
import json
import re
from typing import Dict, Any, List, Optional
import requests
from loguru import logger

# 配置
from core.config import OPENAI_API_KEY, HUGGINGFACE_API_KEY, AZURE_EMOTION_KEY, AZURE_EMOTION_ENDPOINT

# 多语言情感关键词词典
MULTILINGUAL_EMOTION_KEYWORDS = {
    "开心": {
        "zh": ["开心", "快乐", "高兴", "愉快", "兴奋", "喜悦", "欢乐", "爽", "棒", "好"],
        "en": ["happy", "joy", "excited", "pleased", "delighted", "cheerful", "glad", "great", "wonderful"],
        "ja": ["嬉しい", "楽しい", "幸せ", "喜び", "興奮", "愉快", "爽快", "素晴らしい"],
        "ko": ["행복", "기쁨", "즐거움", "신남", "기쁘다", "좋다", "훌륭하다"],
        "fr": ["heureux", "joyeux", "content", "ravi", "excitant", "merveilleux"],
        "de": ["glücklich", "froh", "freudig", "begeistert", "wunderbar"],
        "es": ["feliz", "alegre", "contento", "emocionado", "maravilloso"],
        "ru": ["счастливый", "радостный", "довольный", "восторженный"],
        "ar": ["سعيد", "مبتهج", "مسرور", "متحمس", "رائع"],
        "hi": ["खुश", "आनंदित", "प्रसन्न", "उत्साहित", "शानदार"]
    },
    "悲伤": {
        "zh": ["悲伤", "难过", "伤心", "痛苦", "沮丧", "失望", "绝望", "哭", "泪"],
        "en": ["sad", "sorrow", "grief", "pain", "depressed", "disappointed", "desperate", "cry", "tears"],
        "ja": ["悲しい", "哀しい", "苦しい", "落ち込む", "失望", "絶望", "泣く", "涙"],
        "ko": ["슬픔", "고통", "우울", "실망", "절망", "울다", "눈물"],
        "fr": ["triste", "douleur", "déprimé", "désappointé", "désespéré", "pleurer"],
        "de": ["traurig", "Schmerz", "deprimiert", "enttäuscht", "verzweifelt", "weinen"],
        "es": ["triste", "dolor", "deprimido", "decepcionado", "desesperado", "llorar"],
        "ru": ["грустный", "боль", "подавленный", "разочарованный", "отчаянный"],
        "ar": ["حزين", "ألم", "مكتئب", "خائب", "يائس", "يبكي"],
        "hi": ["दुखी", "दर्द", "उदास", "निराश", "हताश", "रोना"]
    },
    "愤怒": {
        "zh": ["愤怒", "生气", "恼火", "愤怒", "暴躁", "烦躁", "不满", "恨", "讨厌"],
        "en": ["angry", "mad", "furious", "irritated", "annoyed", "hate", "dislike"],
        "ja": ["怒る", "腹立つ", "イライラ", "嫌い", "憎い"],
        "ko": ["화나다", "분노", "짜증", "싫다", "미워하다"],
        "fr": ["fâché", "furieux", "irrité", "agacé", "détester"],
        "de": ["wütend", "verärgert", "gereizt", "hassen", "verabscheuen"],
        "es": ["enojado", "furioso", "irritado", "molesto", "odiar"],
        "ru": ["злой", "сердитый", "раздраженный", "ненавидеть"],
        "ar": ["غاضب", "غضبان", "منزعج", "يكره", "مكروه"],
        "hi": ["गुस्सा", "क्रोधित", "चिढ़ा हुआ", "नफरत", "घृणा"]
    },
    "焦虑": {
        "zh": ["焦虑", "担心", "紧张", "不安", "恐惧", "害怕", "恐慌", "压力", "紧张"],
        "en": ["anxious", "worried", "nervous", "fearful", "scared", "panic", "stress"],
        "ja": ["心配", "不安", "緊張", "恐れる", "怖い", "パニック", "ストレス"],
        "ko": ["걱정", "불안", "긴장", "두려움", "무서움", "패닉", "스트레스"],
        "fr": ["anxieux", "inquiet", "nerveux", "peur", "panique", "stress"],
        "de": ["ängstlich", "besorgt", "nervös", "Angst", "Panik", "Stress"],
        "es": ["ansioso", "preocupado", "nervioso", "miedo", "pánico", "estrés"],
        "ru": ["тревожный", "беспокойный", "нервный", "страх", "паника", "стресс"],
        "ar": ["قلق", "مقلق", "متوتر", "خوف", "ذعر", "توتر"],
        "hi": ["चिंतित", "परेशान", "तनावग्रस्त", "डर", "आतंक", "तनाव"]
    },
    "平静": {
        "zh": ["平静", "冷静", "淡定", "放松", "安宁", "舒适", "轻松", "平和"],
        "en": ["calm", "peaceful", "relaxed", "tranquil", "comfortable", "easy"],
        "ja": ["落ち着く", "静か", "リラックス", "安らか", "快適", "穏やか"],
        "ko": ["차분하다", "평온하다", "편안하다", "안정적", "편리하다"],
        "fr": ["calme", "paisible", "détendu", "tranquille", "confortable"],
        "de": ["ruhig", "friedlich", "entspannt", "bequem", "gelassen"],
        "es": ["tranquilo", "pacífico", "relajado", "cómodo", "sereno"],
        "ru": ["спокойный", "мирный", "расслабленный", "комфортный"],
        "ar": ["هادئ", "سلمي", "مسترخي", "مريح", "مطمئن"],
        "hi": ["शांत", "शांतिपूर्ण", "आरामदायक", "सहज", "सुखद"]
    },
    "中性": {
        "zh": ["一般", "还行", "正常", "普通", "平常", "一般般"],
        "en": ["normal", "okay", "fine", "ordinary", "usual", "alright"],
        "ja": ["普通", "まあまあ", "通常", "一般的", "大丈夫"],
        "ko": ["보통", "괜찮다", "일반적", "평상시", "그럭저럭"],
        "fr": ["normal", "correct", "ordinaire", "habituel", "pas mal"],
        "de": ["normal", "okay", "gewöhnlich", "üblich", "in Ordnung"],
        "es": ["normal", "bien", "ordinario", "habitual", "regular"],
        "ru": ["нормальный", "хорошо", "обычный", "обычно", "нормально"],
        "ar": ["عادي", "حسن", "معتاد", "طبيعي", "مقبول"],
        "hi": ["सामान्य", "ठीक", "साधारण", "सामान्यतः", "बिलकुल"]
    }
}

# 情感强度词汇
INTENSITY_WORDS = {
    "很": 2.0, "非常": 2.0, "特别": 2.0, "极其": 2.5, "超级": 2.5,
    "比较": 1.5, "有点": 1.2, "稍微": 1.1, "略微": 1.1,
    "不": -1.0, "没": -1.0, "无": -1.0
}

def analyze_emotion(text: str, lang: str) -> Tuple[str, str]:
    """
    情感分析主函数
    Args:
        text: 输入文本
        lang: 语言代码
    Returns:
        情感标签
    """
    try:
        # 尝试使用不同的情感分析服务
        emotion = _try_openai_emotion(text, lang)
        if emotion:
            return emotion, "openai"
        else:
            print("【API Service Failed!】openai情感分析失败!")
            
        # emotion = _try_huggingface_emotion(text, lang)
        # if emotion:
        #     return emotion, "huggingface"
        # else:
        #     print("【API Service Failed!】HuggingFace情感分析失败!")
            
        emotion = _try_azure_emotion(text, lang)
        if emotion:
            return emotion, "azure"
        else: 
            print("【API Service Failed!】Azure情感分析失败!")
            
        # 使用规则基础的情感分析
        return _rule_based_emotion_analysis(text, lang), "rule"
        
    except Exception as e:
        logger.error(f"情感分析失败: {e}")
        return "中性", "fallback"

def _try_openai_emotion(text: str, lang: str) -> Optional[str]:
    """使用OpenAI进行情感分析"""
    if not OPENAI_API_KEY:
        return None
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        prompt = f"""
        分析以下文本的情感，从以下选项中选择一个：
        - 开心
        - 悲伤
        - 愤怒
        - 焦虑
        - 平静
        - 中性
        
        用户文本: {text}
        用户语言: {lang}
        
        请只返回对应的情感标签，不要翻译标签，也不要其他内容。
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        emotion = response.choices[0].message.content.strip()
        if emotion in ["开心", "悲伤", "愤怒", "焦虑", "平静", "中性"]:
            return emotion
        return None
    except Exception as e:
        logger.warning(f"OpenAI情感分析失败: {e}")
        return None

def _try_huggingface_emotion(text: str, lang: str) -> Optional[str]:
    """使用HuggingFace进行情感分析"""
    if not HUGGINGFACE_API_KEY:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        # 使用多语言情感分析模型
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        payload = {"inputs": text}
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_name}",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                label = result[0]["label"]
                score = result[0]["score"]
                
                # 映射标签到中文情感
                label_mapping = {
                    "LABEL_0": "悲伤",
                    "LABEL_1": "中性", 
                    "LABEL_2": "开心"
                }
                
                return label_mapping.get(label, "中性")
        
        return None
        
    except Exception as e:
        logger.warning(f"HuggingFace情感分析失败: {e}")
        return None

def _try_azure_emotion(text: str, lang: str) -> Optional[str]:
    """使用Azure Emotion API进行情感分析（文本）"""
    if not AZURE_EMOTION_KEY or not AZURE_EMOTION_ENDPOINT:
        return None
    try:
        url = f"{AZURE_EMOTION_ENDPOINT}/text/analytics/v3.1/sentiment"
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_EMOTION_KEY,
            "Content-Type": "application/json"
        }
        documents = {
            "documents": [
                {"id": "1", "language": lang if lang in ["zh", "en"] else "zh", "text": text}
            ]
        }
        response = requests.post(url, headers=headers, json=documents, timeout=5)
        if response.status_code == 200:
            result = response.json()
            sentiment = result["documents"][0]["sentiment"]
            mapping = {
                "positive": "开心",
                "neutral": "中性",
                "negative": "悲伤"
            }
            return mapping.get(sentiment, "中性")
        else:
            logger.warning(f"Azure Emotion API返回异常: {response.text}")
            return None
    except Exception as e:
        logger.warning(f"Azure Emotion API失败: {e}")
        return None

def _rule_based_emotion_analysis(text: str, lang: str) -> str:
    """基于规则的多语言情感分析"""
    text_lower = text.lower()
    
    # 计算每种情感的得分
    emotion_scores = {}
    
    for emotion, lang_keywords in MULTILINGUAL_EMOTION_KEYWORDS.items():
        score = 0
        # 获取对应语言的关键词
        keywords = lang_keywords.get(lang, lang_keywords.get("zh", []))
        for keyword in keywords:
            if keyword.lower() in text_lower:
                # 检查是否有强度修饰词
                intensity = 1.0
                for intensity_word, multiplier in INTENSITY_WORDS.items():
                    if intensity_word in text_lower:
                        intensity = multiplier
                        break
                
                score += intensity
        
        if score > 0:
            emotion_scores[emotion] = score
    
    # 返回得分最高的情感
    if emotion_scores:
        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        return max_emotion[0]
    
    return "中性"

def get_emotion_details(text: str, lang: str) -> Dict[str, Any]:
    """
    获取详细的情感分析结果
    Args:
        text: 输入文本
        lang: 语言代码
    Returns:
        详细的情感分析结果
    """
    try:
        emotion = analyze_emotion(text, lang)
        
        # 计算情感强度
        intensity = _calculate_emotion_intensity(text, emotion, lang)
        
        # 获取情感建议
        suggestions = _get_emotion_suggestions(emotion)
        
        return {
            "emotion": emotion,
            "intensity": intensity,
            "confidence": 0.8,  # 可以基于实际分析结果调整
            "suggestions": suggestions,
            "text": text,
            "lang": lang
        }
        
    except Exception as e:
        logger.error(f"详细情感分析失败: {e}")
        return {
            "emotion": "中性",
            "intensity": 0.5,
            "confidence": 0.5,
            "suggestions": [],
            "text": text,
            "lang": lang
        }

def _calculate_emotion_intensity(text: str, emotion: str, lang: str = "zh") -> float:
    """计算多语言情感强度"""
    text_lower = text.lower()
    intensity = 0.5  # 默认中等强度
    
    # 基于情感词汇的密度计算强度
    emotion_keywords = MULTILINGUAL_EMOTION_KEYWORDS.get(emotion, {}).get(lang, [])
    keyword_count = sum(1 for keyword in emotion_keywords if keyword.lower() in text_lower)
    
    # 基于文本长度和关键词数量计算强度
    if keyword_count > 0:
        intensity = min(1.0, 0.3 + keyword_count * 0.2)
    
    # 检查强度修饰词
    for intensity_word, multiplier in INTENSITY_WORDS.items():
        if intensity_word in text_lower:
            intensity = min(1.0, intensity * abs(multiplier))
            break
    
    return intensity

def _get_emotion_suggestions(emotion: str) -> List[str]:
    """根据情感获取建议"""
    suggestions = {
        "开心": [
            "继续保持积极的心态",
            "与朋友分享您的快乐",
            "记录下这个美好的时刻"
        ],
        "悲伤": [
            "允许自己感受这种情绪",
            "与信任的人倾诉",
            "尝试一些放松的活动",
            "如果持续感到悲伤，考虑寻求专业帮助"
        ],
        "愤怒": [
            "深呼吸，给自己一些时间冷静",
            "尝试运动来释放压力",
            "避免在愤怒时做重要决定",
            "学习情绪管理技巧"
        ],
        "焦虑": [
            "尝试深呼吸或冥想",
            "列出您担心的事情",
            "专注于当下，不要过度担心未来",
            "如果焦虑持续，考虑寻求专业帮助"
        ],
        "平静": [
            "保持这种平和的状态",
            "享受当下的宁静",
            "可以尝试冥想或瑜伽"
        ],
        "中性": [
            "保持当前的状态",
            "可以尝试一些新的活动来丰富生活"
        ]
    }
    
    return suggestions.get(emotion, [])

def detect_emotion_from_voice(audio_data: bytes) -> str:
    """从语音数据检测情感（需要音频分析）"""
    # TODO: 实现基于音频特征的情感检测
    # 可以使用音频的频谱特征、音调、语速等
    return "中性" 