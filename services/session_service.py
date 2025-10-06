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

import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from sqlmodel import Session, select, update
from loguru import logger

from models.session import AISession, ConversationMessage
from core.db import engine

class SessionManager:
    """AI会话管理器"""
    
    def __init__(self):
        self._active_sessions: Dict[str, AISession] = {}  # 内存中的活跃会话缓存
    
    def _create_session_copy(self, ai_session: AISession) -> AISession:
        """
        创建会话对象的副本，避免SQLAlchemy会话绑定问题
        Args:
            ai_session: 原始会话对象
        Returns:
            会话对象副本
        """
        return AISession(
            id=ai_session.id,
            session_id=ai_session.session_id,
            user_id=ai_session.user_id,
            created_at=ai_session.created_at,
            updated_at=ai_session.updated_at,
            is_active=ai_session.is_active,
            language=ai_session.language,
            voice_style=ai_session.voice_style,
            context_summary=ai_session.context_summary,
            conversation_count=ai_session.conversation_count,
            total_duration=ai_session.total_duration,
            session_metadata=ai_session.session_metadata
        )
    
    def create_session(self, user_id: int, voice_style: Optional[str] = None) -> str:
        """
        创建新的AI会话
        Args:
            user_id: 用户ID
            voice_style: 用户选择的音色
        Returns:
            会话ID
        """
        try:
            session_id = str(uuid.uuid4())
            
            # 创建会话记录（不设置默认语言，等待动态检测）
            ai_session = AISession(
                session_id=session_id,
                user_id=user_id,
                voice_style=voice_style,
                is_active=True
            )
            
            # 保存到数据库
            with Session(engine) as db_session:
                db_session.add(ai_session)
                db_session.commit()
                db_session.refresh(ai_session)
            
            # 添加到内存缓存
            self._active_sessions[session_id] = ai_session
            
            logger.info(f"创建新会话: {session_id} (用户: {user_id})")
            return session_id
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[AISession]:
        """
        获取会话信息
        Args:
            session_id: 会话ID
        Returns:
            会话对象
        """
        try:
            # 先从内存缓存获取
            if session_id in self._active_sessions:
                cached_session = self._active_sessions[session_id]
                # 检查缓存的对象是否仍然有效
                if cached_session and cached_session.is_active:
                    return cached_session
            
            # 从数据库获取
            with Session(engine) as db_session:
                statement = select(AISession).where(AISession.session_id == session_id)
                ai_session = db_session.exec(statement).first()
                
                if ai_session and ai_session.is_active:
                    # 创建新的会话对象副本，避免会话绑定问题
                    session_copy = self._create_session_copy(ai_session)
                    # 添加到内存缓存
                    self._active_sessions[session_id] = session_copy
                    return session_copy
            
            return None
            
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return None
    
    def get_or_create_session(self, user_id: int, session_id: Optional[str] = None, 
                            voice_style: Optional[str] = None) -> str:
        """
        获取或创建会话
        Args:
            user_id: 用户ID
            session_id: 现有会话ID（可选）
            voice_style: 用户选择的音色
        Returns:
            会话ID
        """
        if session_id:
            session = self.get_session(session_id)
            if session and session.user_id == user_id and session.is_active:
                # 更新会话信息（不更新语言，保持动态检测）
                self.update_session_info(session_id, voice_style=voice_style)
                return session_id
        
        # 创建新会话
        return self.create_session(user_id, voice_style)
    
    def update_session_info(self, session_id: str, **kwargs) -> bool:
        """
        更新会话信息
        Args:
            session_id: 会话ID
            **kwargs: 要更新的字段
        Returns:
            是否成功
        """
        try:
            with Session(engine) as db_session:
                statement = select(AISession).where(AISession.session_id == session_id)
                ai_session = db_session.exec(statement).first()
                
                if not ai_session:
                    return False
                
                # 更新字段
                for key, value in kwargs.items():
                    if hasattr(ai_session, key):
                        setattr(ai_session, key, value)
                
                ai_session.update_timestamp()
                db_session.add(ai_session)
                db_session.commit()
                
                # 创建新的会话对象副本，避免会话绑定问题
                session_copy = self._create_session_copy(ai_session)
                
                # 更新内存缓存
                if session_id in self._active_sessions:
                    self._active_sessions[session_id] = session_copy
                
                return True
                
        except Exception as e:
            logger.error(f"更新会话信息失败: {e}")
            return False
    
    def add_message(self, session_id: str, message_type: str, content: str, 
                   intent_id: Optional[int] = None, confidence: Optional[float] = None,
                   emotion: Optional[str] = None, language: str = "zh",
                   processing_time: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加对话消息
        Args:
            session_id: 会话ID
            message_type: 消息类型 (user/ai)
            content: 消息内容
            intent_id: 意图ID
            confidence: 置信度
            emotion: 情感
            language: 语言
            processing_time: 处理时间
            metadata: 元数据
        Returns:
            是否成功
        """
        try:
            # 创建消息记录
            message = ConversationMessage(
                session_id=session_id,
                message_type=message_type,
                content=content,
                intent_id=intent_id,
                confidence=confidence,
                emotion=emotion,
                language=language,
                processing_time=processing_time
            )
            
            if metadata:
                message.set_metadata(metadata)
            
            # 保存到数据库
            with Session(engine) as db_session:
                db_session.add(message)
                
                # 更新会话的对话计数
                statement = select(AISession).where(AISession.session_id == session_id)
                ai_session = db_session.exec(statement).first()
                if ai_session:
                    ai_session.conversation_count += 1
                    ai_session.update_timestamp()
                    db_session.add(ai_session)
                
                db_session.commit()
            
            logger.debug(f"添加消息到会话 {session_id}: {message_type} - {content[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ConversationMessage]:
        """
        获取对话历史
        Args:
            session_id: 会话ID
            limit: 限制数量
        Returns:
            对话消息列表
        """
        try:
            with Session(engine) as db_session:
                statement = select(ConversationMessage).where(
                    ConversationMessage.session_id == session_id
                ).order_by(ConversationMessage.timestamp.desc()).limit(limit)
                
                messages = db_session.exec(statement).all()
                # print('FUCK----------------------------------------------------------------------------------')
                # print(messages)
                return list(reversed(messages))  # 按时间正序返回
                
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    def get_context_summary(self, session_id: str, max_messages: int = 20) -> str:
        """
        生成对话上下文摘要
        Args:
            session_id: 会话ID
            max_messages: 最大消息数量
        Returns:
            上下文摘要
        """
        try:
            messages = self.get_conversation_history(session_id, max_messages)
            if not messages:
                return ""
            
            # 构建上下文摘要
            context_parts = []
            for msg in messages:
                role = "用户" if msg.message_type == "user" else "AI"
                context_parts.append(f"{role}: {msg.content}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"生成上下文摘要失败: {e}")
            return ""
    
    def update_context_summary(self, session_id: str) -> bool:
        """
        更新会话的上下文摘要
        Args:
            session_id: 会话ID
        Returns:
            是否成功
        """
        try:
            summary = self.get_context_summary(session_id)
            return self.update_session_info(session_id, context_summary=summary)
            
        except Exception as e:
            logger.error(f"更新上下文摘要失败: {e}")
            return False
    
    def close_session(self, session_id: str) -> bool:
        """
        关闭会话
        Args:
            session_id: 会话ID
        Returns:
            是否成功
        """
        try:
            with Session(engine) as db_session:
                statement = select(AISession).where(AISession.session_id == session_id)
                ai_session = db_session.exec(statement).first()
                
                if ai_session:
                    ai_session.is_active = False
                    ai_session.update_timestamp()
                    db_session.add(ai_session)
                    db_session.commit()
                    
                    # 从内存缓存移除
                    if session_id in self._active_sessions:
                        del self._active_sessions[session_id]
                    
                    logger.info(f"关闭会话: {session_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"关闭会话失败: {e}")
            return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """
        清理过期会话
        Args:
            max_age_hours: 最大存活时间（小时）
        Returns:
            清理的会话数量
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            with Session(engine) as db_session:
                # 查找过期的活跃会话
                statement = select(AISession).where(
                    AISession.is_active == True,
                    AISession.updated_at < cutoff_time
                )
                expired_sessions = db_session.exec(statement).all()
                
                # 关闭过期会话
                for session in expired_sessions:
                    session.is_active = False
                    session.update_timestamp()
                    db_session.add(session)
                
                db_session.commit()
                
                # 从内存缓存移除
                for session in expired_sessions:
                    if session.session_id in self._active_sessions:
                        del self._active_sessions[session.session_id]
                
                logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
                return len(expired_sessions)
                
        except Exception as e:
            logger.error(f"清理过期会话失败: {e}")
            return 0
    
    def get_user_active_sessions(self, user_id: int) -> List[AISession]:
        """
        获取用户的活跃会话
        Args:
            user_id: 用户ID
        Returns:
            活跃会话列表
        """
        try:
            with Session(engine) as db_session:
                statement = select(AISession).where(
                    AISession.user_id == user_id,
                    AISession.is_active == True
                ).order_by(AISession.updated_at.desc())
                
                return db_session.exec(statement).all()
                
        except Exception as e:
            logger.error(f"获取用户活跃会话失败: {e}")
            return []
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话统计信息
        Args:
            session_id: 会话ID
        Returns:
            统计信息
        """
        try:
            session = self.get_session(session_id)
            if not session:
                return {}
            
            with Session(engine) as db_session:
                # 获取消息统计
                statement = select(ConversationMessage).where(
                    ConversationMessage.session_id == session_id
                )
                messages = db_session.exec(statement).all()
                
                user_messages = [msg for msg in messages if msg.message_type == "user"]
                ai_messages = [msg for msg in messages if msg.message_type == "ai"]
                
                # 计算平均处理时间
                processing_times = [msg.processing_time for msg in ai_messages if msg.processing_time]
                avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
                
                # 计算平均置信度
                confidences = [msg.confidence for msg in ai_messages if msg.confidence]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # 计算语言分布统计
                language_stats = self._calculate_language_distribution(session_id)
                
                return {
                    "session_id": session_id,
                    "user_id": session.user_id,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "total_messages": len(messages),
                    "user_messages": len(user_messages),
                    "ai_messages": len(ai_messages),
                    "conversation_count": session.conversation_count,
                    "total_duration": session.total_duration,
                    "language": session.language,
                    "voice_style": session.voice_style,
                    "avg_processing_time": avg_processing_time,
                    "avg_confidence": avg_confidence,
                    "is_active": session.is_active,
                    "language_distribution": language_stats
                }
                
        except Exception as e:
            logger.error(f"获取会话统计信息失败: {e}")
            return {}
    
    def _calculate_language_distribution(self, session_id: str) -> Dict[str, Any]:
        """
        计算会话中的语言分布
        Args:
            session_id: 会话ID
        Returns:
            语言分布统计
        """
        try:
            with Session(engine) as db_session:
                # 获取所有用户消息的语言
                statement = select(ConversationMessage.language).where(
                    ConversationMessage.session_id == session_id,
                    ConversationMessage.message_type == "user"
                )
                languages = db_session.exec(statement).all()
                
                if not languages:
                    return {"primary_language": None, "language_counts": {}, "total_messages": 0}
                
                # 统计语言使用次数
                language_counts = {}
                for lang in languages:
                    if lang:
                        language_counts[lang] = language_counts.get(lang, 0) + 1
                
                # 找出主要语言（使用次数最多的）
                primary_language = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else None
                
                return {
                    "primary_language": primary_language,
                    "language_counts": language_counts,
                    "total_messages": len(languages)
                }
                
        except Exception as e:
            logger.error(f"计算语言分布失败: {e}")
            return {"primary_language": None, "language_counts": {}, "total_messages": 0}
    
    def update_session_language(self, session_id: str, detected_language: str) -> bool:
        """
        根据语言分布更新会话的主要语言
        Args:
            session_id: 会话ID
            detected_language: 检测到的语言
        Returns:
            是否成功更新
        """
        try:
            # 获取语言分布统计
            language_stats = self._calculate_language_distribution(session_id)
            
            # 如果检测到的语言在历史中占比最高，则更新会话语言
            if (language_stats["primary_language"] == detected_language or 
                language_stats["total_messages"] == 0):
                
                return self.update_session_info(session_id, language=detected_language)
            
            # 否则保持当前主要语言
            return True
            
        except Exception as e:
            logger.error(f"更新会话语言失败: {e}")
            return False

# 全局会话管理器实例
session_manager = SessionManager()
