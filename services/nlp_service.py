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
import statistics
from typing import Tuple, Dict, Any, Optional
import requests
from loguru import logger
from .translation_service import translate_text
import random
import openai

# 配置
from core.config import OPENAI_API_KEY

# 导入通用配置管理器
from utils.config_manager import CONFIG_LOADER
import random

GENERAL_INTENT_ID = 100001

def get_ai_response(text: str, lang: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> Tuple[str, int, float]:
    """
    获取AI回复（支持会话上下文）
    Args:
        text: 用户输入文本
        lang: 语言代码
        session_id: 会话ID
        user_id: 用户ID
    Returns:
        (reply, intent, confidence): AI回复、意图、置信度
    """
    try:
        # 1. 意图识别
        intent_id, confidence = _detect_intent(text, lang)
        
        # 2. 生成带上下文的回复
        reply = generate_reply_with_context(intent_id, text, lang, session_id, user_id)
        
        return reply, intent_id, confidence
        
    except Exception as e:
        logger.error(f"NLP处理失败: {e}")
        return _fallback_response(text, lang)

def _detect_intent(text: str, lang: str) -> Tuple[int, float]:
    """意图识别"""
    try:
        # 使用OpenAI进行意图识别
        if OPENAI_API_KEY:
            intent_id, confidence = _openai_intent_detection(text, lang)   
            if intent_id:
                return intent_id, confidence
            else:
                print("【API Service Failed!】openai意图识别失败!(有API Key)")
        else:
            print("【API Service Failed!】openai意图识别失败!(无API Key)")
        
        # 使用关键词匹配
        return _keyword_intent_detection(text, lang)
        
    except Exception as e:
        logger.error(f"意图识别失败: {e}")
        return GENERAL_INTENT_ID, 0.5

def _openai_intent_detection(text: str, lang: str) -> Tuple[int, float]:
    """使用OpenAI进行意图识别"""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        intent_sheet = CONFIG_LOADER.get_config_sheet("nlp", "Intent")

        prompt = f"""
        分析以下文本的意图，从以下选项中选择（选数字ID）：
        """
        for intent_id, item in intent_sheet.items():
            prompt += f"- {intent_id}: {item.get('Name', '')}, 参考关键词：{item.get('Keywords', '')}\n"
        
        prompt += f"""
        文本: {text}
        语言: {lang}
        
        请返回JSON格式: {{"intent": 意图ID, "confidence": 置信度（0-1）}}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        result = json.loads(response.choices[0].message.content)
        return result["intent"], result["confidence"]
        
    except Exception as e:
        logger.warning(f"OpenAI意图识别失败: {e}")
        return None, 0.5

def _keyword_intent_detection(text: str, lang: str) -> Tuple[int, float]:
    """基于关键词的意图识别"""
    text_lower = text.lower()
    
    # 从配置获取意图关键词
    intent_keywords_sheet = CONFIG_LOADER.get_config_sheet("nlp", "Intent")
    if not intent_keywords_sheet:
        return GENERAL_INTENT_ID, 0.5
    
    for intent_id, item in intent_keywords_sheet.items():
        keywords = item.get('Keywords', [])
        if isinstance(keywords, str):
            # 如果是字符串，尝试解析为列表
            if ',' in keywords:
                keywords = [k.strip() for k in keywords.split(',')]
            else:
                keywords = [keywords]
        elif not isinstance(keywords, list):
            keywords = []
        
        for keyword in keywords:
            if keyword in text_lower:
                # 计算置信度（基于匹配的关键词数量）
                matches = sum(1 for k in keywords if k in text_lower)
                confidence = min(0.9, 0.5 + matches * 0.1)
                return intent_id, confidence
    
    return GENERAL_INTENT_ID, 0.5

def _fallback_response(text: str, lang: str) -> Tuple[str, int, float]:
    """备用回复"""
    return "抱歉，我现在无法处理您的请求。请稍后再试。", GENERAL_INTENT_ID, 0.3

def _get_page_context(route: str) -> str:
    """获取页面上下文信息（基于新版 page_ui_info.xlsx 表结构）"""
    try:
        # 1) 页面基础信息 - pages
        page_info = CONFIG_LOADER.get_config_value("page_ui_info", "pages", route) or {}
        page_name = page_info.get('page_name', '未知页面')
        # category = page_info.get('category', '')
        description = page_info.get('description', '')
        tags = page_info.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        statistics = page_info.get('statistics', '')

        # 2) 健康与业务数据字段 - fields（按route过滤）
        # fields_sheet = CONFIG_LOADER.get_config_sheet("page_ui_info", "fields") or {}
        # field_lines = []
        # for _, field in fields_sheet.items():
        #     if field.get('route') != route:
        #         continue
        #     display_name = field.get('display_name', field.get('field_id', ''))
        #     data_type = field.get('data_type', '')
        #     unit = field.get('unit', '')
        #     fmt = field.get('format', '')
        #     desc = field.get('description', '')
        #     example = field.get('example', '')
        #     synonyms = field.get('synonyms', [])
        #     if isinstance(synonyms, str):
        #         synonyms = [s.strip() for s in synonyms.split(',') if s.strip()]
        #     # 行内拼装（保守长度，便于投喂大模型）
        #     parts = [f"{display_name}"]
        #     if desc:
        #         parts.append(f"{desc}")
        #     meta = []
        #     if data_type:
        #         meta.append(f"类型:{data_type}")
        #     if unit:
        #         meta.append(f"单位:{unit}")
        #     if fmt:
        #         meta.append(f"显示:{fmt}")
        #     if example not in (None, ''):
        #         meta.append(f"示例:{example}")
        #     if synonyms:
        #         meta.append(f"同义:{' / '.join(synonyms)}")
        #     if meta:
        #         parts.append(f"({'，'.join(meta)})")
        #     field_lines.append(f"- " + " ".join(parts))

        # 3) UI组件 - components（按route过滤）
        comps_sheet = CONFIG_LOADER.get_config_sheet("page_ui_info", "components") or {}
        comp_lines = []
        for _, comp in comps_sheet.items():
            if comp.get('route') != route:
                continue
            name = comp.get('name', comp.get('component_id', '组件'))
            ctype = comp.get('type', '')
            disp = comp.get('display', '')
            desc = comp.get('description', '')
            related_fields = comp.get('related_fields', [])
            if isinstance(related_fields, str):
                related_fields = [f.strip() for f in related_fields.split(',') if f.strip()]
            comp_meta = []
            if ctype:
                comp_meta.append(f"类型:{ctype}")
            if disp:
                comp_meta.append(f"内容:{disp}")
            if related_fields:
                comp_meta.append(f"字段:{' / '.join(related_fields)}")
            line = f"- {name}"
            if desc:
                line += f"：{desc}"
            if comp_meta:
                line += f"（{'，'.join(comp_meta)}）"
            comp_lines.append(line)

        # 4) 页面操作 - actions（按route过滤、摘要化）
        actions_sheet = CONFIG_LOADER.get_config_sheet("page_ui_info", "actions") or {}
        action_lines = []
        for _, act in actions_sheet.items():
            if act.get('route') != route:
                continue
            aname = act.get('name', act.get('action_id', '操作'))
            atype = act.get('type', '')
            trig = act.get('trigger', '')
            result = act.get('result', '')
            related = act.get('related', [])
            if isinstance(related, str):
                related = [r.strip() for r in related.split(',') if r.strip()]
            meta = []
            if atype:
                meta.append(f"类型:{atype}")
            if trig:
                meta.append(f"触发:{trig}")
            if related:
                meta.append(f"涉及:{' / '.join(related)}")
            line = f"- {aname}"
            if result:
                line += f" → {result}"
            if meta:
                line += f"（{'，'.join(meta)}）"
            action_lines.append(line)

        # 5) 页面状态 - states（按route过滤、枚举值）
        # states_sheet = CONFIG_LOADER.get_config_sheet("page_ui_info", "states") or {}
        # state_lines = []
        # for _, st in states_sheet.items():
        #     if st.get('route') != route:
        #         continue
        #     sname = st.get('name', st.get('state_id', '状态'))
        #     stype = st.get('type', '')
        #     values = st.get('values', [])
        #     if isinstance(values, str):
        #         values = [v.strip() for v in values.split(',') if v.strip()]
        #     desc = st.get('description', '')
        #     line = f"- {sname}"
        #     meta = []
        #     if stype:
        #         meta.append(f"类型:{stype}")
        #     if values:
        #         meta.append(f"取值:{' / '.join(values)}")
        #     if meta:
        #         line += f"（{'，'.join(meta)}）"
        #     if desc:
        #         line += f"：{desc}"
        #     state_lines.append(line)

        # # 6) 追加页面提示词 - prompts（可选）
        # prompts_sheet = CONFIG_LOADER.get_config_sheet("page_ui_info", "prompts") or {}
        # page_prompt = ""
        # for _, pr in prompts_sheet.items():
        #     if pr.get('route') == route:
        #         page_prompt = pr.get('prompt', '')
        #         break

        # 统一拼装上下文文本
        ctx = []
        head = f"用户当前在页面: {page_name} ({route})"
        # if category:
        #     head += f"，分类: {category}"
        if tags:
            head += f"，标签: {' / '.join(tags)}"
        if statistics:
            head += f"，统计数据: {statistics}"
        ctx.append(head)
        if description:
            ctx.append(f"页面描述: {description}")

        # if field_lines:
        #     ctx.append("页面数据字段:")
        #     ctx.extend(field_lines[:40])  # 控制最大条数，避免提示过长

        if comp_lines:
            ctx.append("页面UI组件:")
            ctx.extend(comp_lines[:30])

        if action_lines:
            ctx.append("页面可执行操作:")
            ctx.extend(action_lines[:20])

        # if state_lines:
        #     ctx.append("页面状态信息:")
        #     ctx.extend(state_lines[:20])

        # if page_prompt:
        #     ctx.append("页面提示:")
        #     ctx.append(page_prompt)

        return "\n".join(ctx) if ctx else f"用户当前在页面: {route}"

    except Exception as e:
        logger.error(f"获取页面上下文失败: {e}")
        return f"用户当前在页面: {route}"

def analyze_sentiment(text: str, lang: str) -> Dict[str, Any]:
    """情感分析"""
    try:
        # 简单的情感分析
        positive_words = ["好", "棒", "开心", "快乐", "满意", "喜欢"]
        negative_words = ["不好", "糟糕", "难过", "痛苦", "失望", "讨厌"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = 0.7
        elif negative_count > positive_count:
            sentiment = "negative"
            score = 0.3
        else:
            sentiment = "neutral"
            score = 0.5
            
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_count": positive_count,
            "negative_count": negative_count
        }
        
    except Exception as e:
        logger.error(f"情感分析失败: {e}")
        return {"sentiment": "neutral", "score": 0.5} 

def generate_reply(intent_id, user_input, lang, session_id, user_id, current_page=None):
    """生成基础回复（无上下文）"""
    return generate_reply_with_context(intent_id, user_input, lang, session_id, user_id, current_page)

def generate_reply_with_context(intent_id, user_input, lang, session_id, user_id, current_page=None):
    """生成带上下文的回复"""
    # 检查intent_id是否有效
    if intent_id is None:
        logger.error(f"意图ID为空")
        return "很抱歉，我还不太明白你的意思。"
    
    intent_config = CONFIG_LOADER.get_config_value("nlp", "Intent", intent_id)
    if intent_config is None:
        logger.error(f"意图ID为{intent_id}的配置不存在")
        return "很抱歉，我还不太明白你的意思。"
    
    intent_desc = intent_config.get('Description', '未知意图')
    
    # 获取当前页面信息
    page_context = ""
    if current_page:
        current_route = current_page.get('route', '')
        page_context = _get_page_context(current_route)
        logger.info(f"当前页面: {current_route}, 页面上下文: {page_context}")
    
    print("page_context --> ", page_context)

    templates = [""]
    if intent_config.get("Catagory", "") == "chat":
    # 从配置获取回复模板
        templates_sheet = CONFIG_LOADER.get_config_sheet("nlp", "Chat")
        templates = []
        if templates_sheet and intent_id in templates_sheet:
            template_item = templates_sheet[intent_id]
            template_str = template_item.get('Template', '')
            if isinstance(template_str, str):
                if '\n' in template_str:
                    templates = [t.strip() for t in template_str.split('\n') if t.strip()]
                else:
                    templates = [template_str]
            elif isinstance(template_str, list):
                templates = template_str
            else:
                templates = ["很抱歉，我还不太明白你的意思。"]
        else:
            templates = ["很抱歉，我还不太明白你的意思。"]
    else:
        templates = ["好的，我明白了，马上帮你导航到..."]
    
    base_reply = random.choice(templates)
    
    # 从配置获取知识建议
    knowledge_sheet = CONFIG_LOADER.get_config_sheet("nlp", "Chat")
    suggestion = ""
    if knowledge_sheet and intent_id in knowledge_sheet:
        knowledge_item = knowledge_sheet[intent_id]
        content = knowledge_item.get('Knowledge', '')
        if isinstance(content, str):
            suggestion = content
        elif isinstance(content, list) and content:
            suggestion = str(content)
    
    # 获取会话上下文
    context_info = ""
    if session_id:
        try:
            from services.session_service import session_manager
            # 获取对话历史
            history = session_manager.get_conversation_history(session_id, limit=20)
            # for i in range(100):
            #     print("history --> ", history)
            if history:
                context_parts = []
                for msg in history[-15:]:  # 只取最近15条消息作为上下文
                    role = "用户" if msg.message_type == "user" else "AI"
                    context_parts.append(f"{role}: {msg.content}")
                context_info = "\n".join(context_parts)
                logger.info(f"使用会话上下文: {len(history)} 条历史消息")
        except Exception as e:
            logger.warning(f"获取会话上下文失败: {e}")
    
    # 构建增强的提示词
    system_prompt = "你是一个温暖、积极探讨的、拥有一定知识的聊天朋友。"
    
    user_prompt = (
        f"用户说：{user_input}\n"
        f"**回答语言：{lang}**\n"
    )
    
    # 添加页面上下文信息
    if page_context:
        user_prompt += f"**当前用户所在页面信息：**\n{page_context}\n"
    
    # user_prompt += (
    #     f"**其他要求：**\n"
    #     f"1. 结合对话上下文和当前页面信息\n"
    #     f"2. 请像一个人一样积极温暖地回答用户的询问，如果用户询问数据信息则温和地结合解读和鼓励等，不要仅仅念数字条目。最后必要时在最后询问延伸用户的话题\n"
    #     f"3. 如果用户表示导航意图，如果当前页面不是目标页面，则告诉他你会帮他导航到目标页面即可，如果当前页面是目标页面，则告诉他你已经在这个页面了\n"
    #     f"3. 必须保证使用完全专业的术语，不要说无用的口水话，如果信息不足则积极询问\n"
    #     f"4. 回复尽量简洁，尽量不超过100字，除非用户提现需要详尽信息的意图\n"
    #     f"5. 积极获取更多信息，尽可能委婉地引导用户提供信息，但必须用人文关怀的态度询问\n"
    #     f"6. 注意：回复一定要用回答语言{lang}回答!!!\n"
    #     f"7. 请一定要参考对话上下文保持对话的连贯性，如果用户问之前的相关内容，请参考上下文\n"
    #     f"8. 如果用户询问当前页面的具体信息（如健康数据、UI组件等），请基于页面上下文信息进行回答\n"
    #     f"9. 如果用户询问页面上的某个数据或功能，请结合页面上下文提供准确的解释\n"    
    # )

    user_prompt += (
    f"**Role Definition:**\n"
    f"1. You are a trusted friend and a confidante\n"
    f"2. You are highly skilled in active listening\n"
    f"3. You build a heart-to-heart connection with users\n"
    f"4. You take as much time as needed and encourage users to talk about and talk through their emotional woes or share their happiness, events, and experiences\n"
    f"5. You listen intently to both the tone and the words, including subtexts from the user, and ask clarifying questions to better understand their needs\n"
    f"6. You offer a sounding board, a shoulder to lean on, a place to unburden themselves, and a guiding hand in emotion regulation for users\n\n"

    f"**Voice Tone:**\n"
    f"- Warm, trusting, caring, affectionate, confident\n"
    f"- Use conversational language\n\n"

    f"**Guidelines:**\n"
    f"- Do not lecture\n"
    f"- Do not provide generic responses\n"
    f"- Do not cut short the dialogue before guiding users out of their negative mood\n\n"

    f"**Interaction Flow:**\n"
    f"- After a user signs in, immediately greet them with: 'how are you doing, (first name)?'\n"
    f"- Induce them into a dialogue to talk about their mood and what’s going on\n"
    f"- Take time in dialogue and do not rush\n"
    f"- Reference all previous dialogues and user-specific data/feedback to make the conversation feel like a real-life talk with a close friend\n\n"

    f"**After Emotional Support:**\n"
    f"- Once the user is guided into a positive mood, navigate to the dashboard screen\n"
    f"- Highlight 3-4 things (e.g., something done well, something to improve, or a key reminder)\n"
    f"- If the user wants to explore an item further, navigate to the appropriate screen and provide relevant insights and data (focus on actionable insights, not reading data line by line)\n\n"

    f"**Guidance Approach:**\n"
    f"- Based on actionable insights, take the lead in suggesting specific activities to add or things to reduce/avoid\n"
    f"- Do not burden the user with unnecessary decision-making\n"
    f"- After the user tries suggested activities, ask for feedback and adapt future suggestions accordingly\n"
    f"- Gently remind users of their agenda and suggest additional activities to further improve mood and health\n"
)
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        messages = [{"role": "system", "content": system_prompt}]
        
        # 如果有上下文，添加历史消息
        if context_info:
            try:
                from services.session_service import session_manager
                history = session_manager.get_conversation_history(session_id, limit=20)
                for msg in history:
                    role = "user" if msg.message_type == "user" else "assistant"
                    messages.append({"role": role, "content": msg.content})
            except Exception as e:
                logger.warning(f"添加历史消息失败: {e}")
        
        messages.append({"role": "user", "content": user_prompt})
        
        print("---------------------------------------- start -----------------------------------------------")
        print(context_info)
        print("---------------------------------------- mid -----------------------------------------------")
        for message in messages:
            print(message)
        print("--------------------------------------- end ------------------------------------------------")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_completion_tokens=1000,
            # temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"生成回复失败: {e}")
        return base_reply 