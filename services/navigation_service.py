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

import re
import json
import openai
from typing import Dict, List, Tuple, Optional, Any
from loguru import logger
from utils.config_manager import CONFIG_LOADER
from core.config import OPENAI_API_KEY


class NavigationService:
    """AI语音导航服务"""
    
    def __init__(self):
        self.pages_config = {}
        self.actions_config = {}
        self._load_configs()
    
    def _load_configs(self):
        """加载导航配置"""
        try:
            # 加载页面配置
            pages_sheet = CONFIG_LOADER.get_config_sheet("navigation", "Pages")
            if pages_sheet:
                self.pages_config = pages_sheet
            
            # 加载动作配置
            actions_sheet = CONFIG_LOADER.get_config_sheet("navigation", "Actions")
            if actions_sheet:
                self.actions_config = actions_sheet
                
        except Exception as e:
            logger.error(f"加载导航配置失败: {e}")
    
    def detect_navigation_intent(self, text: str, lang: str) -> Tuple[Dict[str, Any], str]:
        """
        检测导航意图
        Args:
            text: 用户输入文本
            lang: 语言代码
        Returns:
            导航结果字典
        """
        try:
            # 1. 首先尝试使用OpenAI检测
            openai_result = self._detect_with_openai(text, lang)
            if openai_result and openai_result.get("confidence", 0) > 0.7:
                return openai_result, "openai"
            
            # 2. OpenAI检测失败或置信度低，使用关键词检测作为备选
            logger.info("使用关键词检测作为备选方案")
            return self._detect_with_keywords(text, lang), "fallback"
            
        except Exception as e:
            logger.error(f"导航意图检测失败: {e}")
            return {
                "type": "error",
                "action": None,
                "confidence": 0.0,
                "message": "导航检测出错"
            }, "error"
    
    def _detect_with_openai(self, text: str, lang: str) -> Optional[Dict[str, Any]]:
        """使用OpenAI检测导航意图"""
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)

            # 构建可用页面和动作的提示
            pages_info = []
            for page_id, page_config in self.pages_config.items():
                pages_info.append({
                    "id": page_id,
                    "name": page_config.get('Name', ''),
                    "route": page_config.get('Route', ''),
                    "screen_class": page_config.get('ScreenClass', ''),
                    "keywords": page_config.get('Keywords', ''),
                    "description": page_config.get('Description', '')
                })
            
            actions_info = []
            for action_id, action_config in self.actions_config.items():
                actions_info.append({
                    "id": action_id,
                    "name": action_config.get('Name', ''),
                    "action": action_config.get('Action', ''),
                    "keywords": action_config.get('Keywords', ''),
                    "description": action_config.get('Description', '')
                })
            
            # 构建系统提示
            system_prompt = f"""
你是一个导航意图识别助手。根据用户输入，判断用户想要导航到哪个页面或执行什么动作。一般来说，当用户说“我要转到...“，"跳转到...“，"我要看...“等命令语句以及“页面”，“界面”等词语时置信度应当很高。

可用页面：
{json.dumps(pages_info, ensure_ascii=False, indent=2)}

可用动作：
{json.dumps(actions_info, ensure_ascii=False, indent=2)}

请分析用户输入，返回JSON格式的导航结果：
- 如果是页面导航，返回：{{"type": "page_navigation", "target": 页面ID, "confidence": 置信度0-1}}
- 如果是动作执行，返回：{{"type": "action", "action": "动作名称", "confidence": 置信度0-1}}
- 如果无导航意图，返回：{{"type": "none", "confidence": 0}}

只返回JSON，不要其他内容。
"""

            # 调用OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=200
            )
            
            # 解析响应
            result_text = response.choices[0].message.content.strip()
            try:
                result = json.loads(result_text)
                
                # 根据类型构建完整结果
                if result.get("type") == "page_navigation":
                    target_id = result.get("target")
                    if target_id and target_id in self.pages_config:
                        page_config = self.pages_config[target_id]
                        return {
                            "type": "page_navigation",
                            "action": "navigate",
                            "target": target_id,
                            "route": page_config.get('Route', ''),
                            "screen_class": page_config.get('ScreenClass', ''),
                            "name": page_config.get('Name', ''),
                            "confidence": result.get("confidence", 0.8),
                            "message": f"正在为您导航到{page_config.get('Name', '')}"
                        }
                
                elif result.get("type") == "action":
                    action_name = result.get("action")
                    # 查找对应的动作配置
                    for action_id, action_config in self.actions_config.items():
                        if action_config.get('Action') == action_name:
                            return {
                                "type": "action",
                                "action": action_name,
                                "parameters": action_config.get('Parameters', {}),
                                "name": action_config.get('Name', ''),
                                "confidence": result.get("confidence", 0.8),
                                "message": f"正在执行{action_config.get('Name', '')}操作"
                            }
                
                elif result.get("type") == "none":
                    return {
                        "type": "none",
                        "action": None,
                        "confidence": 0.0,
                        "message": "未识别到导航意图"
                    }
                    
            except json.JSONDecodeError as e:
                logger.error(f"解析OpenAI响应失败: {e}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI检测失败: {e}")
            return None
    
    def _detect_with_keywords(self, text: str, lang: str) -> Dict[str, Any]:
        """使用关键词检测导航意图（备选方案）"""
        # 1. 检测页面导航意图
        page_result = self._detect_page_navigation(text, lang)
        if page_result:
            return {
                "type": "page_navigation",
                "action": "navigate",
                "target": page_result["page_id"],
                "route": page_result["route"],
                "screen_class": page_result["screen_class"],
                "name": page_result["name"],
                "confidence": page_result["confidence"],
                "message": f"正在为您导航到{page_result['name']}"
            }
        
        # 2. 检测动作意图
        action_result = self._detect_action_intent(text, lang)
        if action_result:
            return {
                "type": "action",
                "action": action_result["action"],
                "parameters": action_result["parameters"],
                "name": action_result["name"],
                "confidence": action_result["confidence"],
                "message": f"正在执行{action_result['name']}操作"
            }
        
        # 3. 无导航意图
        return {
            "type": "none",
            "action": None,
            "confidence": 0.0,
            "message": "未识别到导航意图"
        }
    
    def _detect_page_navigation(self, text: str, lang: str) -> Optional[Dict[str, Any]]:
        """检测页面导航意图"""
        if not self.pages_config:
            return None
        
        best_match = None
        best_score = 0.0
        
        for page_id, page_config in self.pages_config.items():
            # 检查页面名称匹配
            page_name = page_config.get('Name', '')
            if page_name and page_name.lower() in text.lower():
                score = len(page_name) / len(text) * 1.5  # 名称匹配权重更高
                if score > best_score:
                    best_score = score
                    best_match = {
                        "page_id": page_id,
                        "route": page_config.get('Route', ''),
                        "screen_class": page_config.get('ScreenClass', ''),
                        "name": page_name,
                        "confidence": min(score, 1.0)
                    }
            
            # 检查关键词匹配
            keywords = page_config.get('Keywords', '')
            if keywords:
                keyword_list = [k.strip() for k in keywords.split(',')]
                for keyword in keyword_list:
                    if keyword and keyword.lower() in text.lower():
                        score = len(keyword) / len(text)
                        if score > best_score:
                            best_score = score
                            best_match = {
                                "page_id": page_id,
                                "route": page_config.get('Route', ''),
                                "screen_class": page_config.get('ScreenClass', ''),
                                "name": page_config.get('Name', ''),
                                "confidence": min(score, 1.0)
                            }
        
        return best_match if best_score > 0.3 else None
    
    def _detect_action_intent(self, text: str, lang: str) -> Optional[Dict[str, Any]]:
        """检测动作意图"""
        if not self.actions_config:
            return None
        
        best_match = None
        best_score = 0.0
        
        for action_id, action_config in self.actions_config.items():
            # 检查动作名称匹配
            action_name = action_config.get('Name', '')
            if action_name and action_name.lower() in text.lower():
                score = len(action_name) / len(text) * 1.5
                if score > best_score:
                    best_score = score
                    best_match = {
                        "action": action_config.get('Action', ''),
                        "parameters": action_config.get('Parameters', {}),
                        "name": action_name,
                        "confidence": min(score, 1.0)
                    }
            
            # 检查关键词匹配
            keywords = action_config.get('Keywords', '')
            if keywords:
                keyword_list = [k.strip() for k in keywords.split(',')]
                for keyword in keyword_list:
                    if keyword and keyword.lower() in text.lower():
                        score = len(keyword) / len(text)
                        if score > best_score:
                            best_score = score
                            best_match = {
                                "action": action_config.get('Action', ''),
                                "parameters": action_config.get('Parameters', {}),
                                "name": action_config.get('Name', ''),
                                "confidence": min(score, 1.0)
                            }
        
        return best_match if best_score > 0.3 else None
    
    def get_available_pages(self) -> List[Dict[str, Any]]:
        """获取所有可用页面"""
        pages = []
        for page_id, page_config in self.pages_config.items():
            pages.append({
                "id": page_id,
                "name": page_config.get('Name', ''),
                "route": page_config.get('Route', ''),
                "screen_class": page_config.get('ScreenClass', ''),
                "description": page_config.get('Description', ''),
                "icon": page_config.get('Icon', ''),
                "category": page_config.get('Category', '')
            })
        return pages
    
    def get_page_by_route(self, route: str) -> Optional[Dict[str, Any]]:
        """根据路由获取页面信息"""
        for page_id, page_config in self.pages_config.items():
            if page_config.get('Route') == route:
                return {
                    "id": page_id,
                    "name": page_config.get('Name', ''),
                    "route": route,
                    "screen_class": page_config.get('ScreenClass', ''),
                    "description": page_config.get('Description', ''),
                    "icon": page_config.get('Icon', ''),
                    "category": page_config.get('Category', '')
                }
        return None
    
    def reload_configs(self):
        """重新加载配置"""
        self._load_configs()
        logger.info("导航配置已重新加载")

# 全局导航服务实例
navigation_service = NavigationService() 