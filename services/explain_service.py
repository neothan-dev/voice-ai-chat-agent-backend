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
import re
from typing import Dict, Any, List, Optional
import requests
from loguru import logger
from typing import Tuple

# 配置
from core.config import OPENAI_API_KEY

def explain_response(text: str, reply: str, intent: str, emotion: str, lang: str) -> Tuple[str, str]:
    """
    解释AI回复的决策过程
    Args:
        text: 用户输入文本
        reply: AI回复
        intent: 识别的意图
        emotion: 检测的情感
    Returns:
        解释文本
    """
    try:
        # 尝试使用OpenAI生成解释
        explain = _openai_explanation(text, reply, intent, emotion, lang)
        if explain:
            return explain, "openai"
        else:
            print("【API Service Failed!】openai解释生成失败!")
        
        explain = _rule_based_explanation(text, reply, intent, emotion)
        return explain, "fallback"
        
    except Exception as e:
        logger.error(f"可解释性分析失败: {e}")
        return _fallback_explanation(text, reply, intent, emotion), "fallback"

def _openai_explanation(text: str, reply: str, intent: str, emotion: str, lang: str) -> str:
    """使用OpenAI生成解释"""
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        作为AI健康助手，请解释为什么我会这样回复用户。
        
        用户输入: {text}
        AI回复: {reply}
        识别意图: {intent}
        检测情感: {emotion}
        
        请简要解释：
        1. 为什么识别出这个意图
        2. 为什么检测到这种情感
        3. 为什么给出这样的回复
        4. 这个回复如何帮助用户
        
        请用简洁的{lang}回答，不超过100字。
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.warning(f"OpenAI解释生成失败: {e}")
        return None

def _rule_based_explanation(text: str, reply: str, intent: str, emotion: str) -> str:
    """基于规则的解释生成"""
    explanations = []
    
    # 意图解释
    intent_explanations = {
        "greeting": "用户与AI进行问候或寒暄，AI会以友好、积极的方式回应，营造良好互动氛围。",
        "health_advice": "根据您提到的健康相关内容，我识别出您需要健康建议",
        "weather": "您询问了天气相关信息，我识别出天气查询意图",
        "mood": "您表达了情绪状态，我识别出情感关怀意图",
        "exercise": "您提到了运动相关内容，我识别出运动指导意图",
        "diet": "您询问了饮食相关问题，我识别出营养建议意图",
        "sleep": "您提到了睡眠相关内容，我识别出睡眠指导意图",
        "medical": "您提到了医疗相关问题，我识别出医疗咨询意图",
        "general": "我识别出这是一般性对话"
    }
    
    if intent in intent_explanations:
        explanations.append(intent_explanations[intent])
    
    # 情感解释
    emotion_explanations = {
        "开心": "检测到您的心情比较愉快",
        "悲伤": "检测到您可能有些低落",
        "愤怒": "检测到您可能有些不满",
        "焦虑": "检测到您可能有些担心",
        "平静": "检测到您的心情比较平静",
        "中性": "检测到您的心情比较中性"
    }
    
    if emotion in emotion_explanations:
        explanations.append(emotion_explanations[emotion])
    
    # 回复解释
    reply_explanations = {
        "greeting": "AI通过问候语拉近与用户的距离，体现人文关怀。",
        "health_advice": "因此我提供了相关的健康建议来帮助您",
        "weather": "因此我建议您查看天气预报获取准确信息",
        "mood": "因此我提供了情感支持和建议",
        "exercise": "因此我提供了运动指导建议",
        "diet": "因此我提供了营养饮食建议",
        "sleep": "因此我提供了睡眠改善建议",
        "medical": "因此我建议您咨询专业医生",
        "general": "因此我提供了友好的回应"
    }
    
    if intent in reply_explanations:
        explanations.append(reply_explanations[intent])
    
    if explanations:
        return "。".join(explanations) + "。"
    else:
        return f"基于您的输入'{text}'和检测到的情感'{emotion}'，我提供了相应的回复和建议。"

def _fallback_explanation(text: str, reply: str, intent: str, emotion: str) -> str:
    """备用解释"""
    return f"我根据您的输入'{text}'，结合检测到的情感'{emotion}'和意图'{intent}'，提供了相应的回复。"

def explain_ai_decision(features: Dict[str, Any], prediction: str, confidence: float) -> Dict[str, Any]:
    """
    解释AI决策过程
    Args:
        features: 输入特征
        prediction: 预测结果
        confidence: 置信度
    Returns:
        决策解释
    """
    try:
        explanation = {
            "prediction": prediction,
            "confidence": confidence,
            "key_features": _extract_key_features(features),
            "reasoning": _generate_reasoning(features, prediction),
            "limitations": _identify_limitations(confidence),
            "recommendations": _provide_recommendations(prediction, confidence)
        }
        
        return explanation
        
    except Exception as e:
        logger.error(f"AI决策解释失败: {e}")
        return {
            "prediction": prediction,
            "confidence": confidence,
            "error": "解释生成失败"
        }

def _extract_key_features(features: Dict[str, Any]) -> List[str]:
    """提取关键特征"""
    key_features = []
    
    # 根据特征类型提取关键信息
    if "text_length" in features:
        if features["text_length"] > 50:
            key_features.append("长文本输入")
        else:
            key_features.append("短文本输入")
    
    if "keywords" in features:
        key_features.extend(features["keywords"][:3])  # 前3个关键词
    
    if "sentiment" in features:
        key_features.append(f"情感倾向: {features['sentiment']}")
    
    return key_features

def _generate_reasoning(features: Dict[str, Any], prediction: str) -> str:
    """生成推理过程"""
    reasoning_parts = []
    
    if "intent" in features:
        reasoning_parts.append(f"识别到意图: {features['intent']}")
    
    if "emotion" in features:
        reasoning_parts.append(f"检测到情感: {features['emotion']}")
    
    if "keywords" in features and features["keywords"]:
        reasoning_parts.append(f"关键信息: {', '.join(features['keywords'][:3])}")
    
    reasoning_parts.append(f"因此生成回复: {prediction}")
    
    return " → ".join(reasoning_parts)

def _identify_limitations(confidence: float) -> List[str]:
    """识别局限性"""
    limitations = []
    
    if confidence < 0.7:
        limitations.append("置信度较低，建议用户提供更多信息")
    
    if confidence < 0.5:
        limitations.append("可能存在理解偏差，建议用户重新表述")
    
    limitations.append("AI回复仅供参考，不能替代专业医疗建议")
    
    return limitations

def _provide_recommendations(prediction: str, confidence: float) -> List[str]:
    """提供建议"""
    recommendations = []
    
    if confidence < 0.8:
        recommendations.append("如果回复不够准确，请提供更详细的信息")
    
    if "medical" in prediction.lower():
        recommendations.append("如有健康问题，建议咨询专业医生")
    
    recommendations.append("可以继续提问以获得更多帮助")
    
    return recommendations

def explain_model_behavior(model_name: str, input_data: Any, output: Any) -> Dict[str, Any]:
    """
    解释模型行为
    Args:
        model_name: 模型名称
        input_data: 输入数据
        output: 输出结果
    Returns:
        模型行为解释
    """
    try:
        explanation = {
            "model": model_name,
            "input_analysis": _analyze_input(input_data),
            "output_analysis": _analyze_output(output),
            "model_characteristics": _get_model_characteristics(model_name),
            "potential_biases": _identify_potential_biases(model_name),
            "fairness_assessment": _assess_fairness(input_data, output)
        }
        
        return explanation
        
    except Exception as e:
        logger.error(f"模型行为解释失败: {e}")
        return {
            "model": model_name,
            "error": "解释生成失败"
        }

def _analyze_input(input_data: Any) -> Dict[str, Any]:
    """分析输入数据"""
    if isinstance(input_data, str):
        return {
            "type": "text",
            "length": len(input_data),
            "language": _detect_language_simple(input_data),
            "sentiment": _analyze_sentiment_simple(input_data)
        }
    else:
        return {
            "type": "unknown",
            "data": str(input_data)
        }

def _analyze_output(output: Any) -> Dict[str, Any]:
    """分析输出结果"""
    if isinstance(output, str):
        return {
            "type": "text",
            "length": len(output),
            "tone": _analyze_tone(output)
        }
    else:
        return {
            "type": "unknown",
            "data": str(output)
        }

def _get_model_characteristics(model_name: str) -> List[str]:
    """获取模型特征"""
    characteristics = {
        "gpt-3.5-turbo": [
            "基于大规模语言模型",
            "支持多语言理解",
            "具有上下文理解能力",
            "可能产生幻觉"
        ],
        "whisper": [
            "语音识别模型",
            "支持多语言",
            "对噪音敏感"
        ],
        "default": [
            "基于规则的模型",
            "响应速度快",
            "可解释性强"
        ]
    }
    
    return characteristics.get(model_name, characteristics["default"])

def _identify_potential_biases(model_name: str) -> List[str]:
    """识别潜在偏见"""
    biases = [
        "训练数据可能存在偏见",
        "可能反映训练数据的文化背景",
        "对某些群体的理解可能不够准确"
    ]
    
    return biases

def _assess_fairness(input_data: Any, output: Any) -> Dict[str, Any]:
    """评估公平性"""
    return {
        "score": 0.8,  # 公平性评分
        "concerns": [
            "需要更多样化的训练数据",
            "应定期进行公平性评估"
        ],
        "recommendations": [
            "收集更多样化的用户反馈",
            "定期更新模型训练数据"
        ]
    }

def _detect_language_simple(text: str) -> str:
    """简单语言检测"""
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        return "中文"
    else:
        return "英文"

def _analyze_sentiment_simple(text: str) -> str:
    """简单情感分析"""
    positive_words = ["好", "棒", "开心", "快乐"]
    negative_words = ["不好", "糟糕", "难过", "痛苦"]
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "积极"
    elif negative_count > positive_count:
        return "消极"
    else:
        return "中性"

def _analyze_tone(text: str) -> str:
    """分析语调"""
    if "建议" in text or "推荐" in text:
        return "建议性"
    elif "?" in text or "？" in text:
        return "疑问性"
    elif "!" in text or "！" in text:
        return "强调性"
    else:
        return "陈述性" 