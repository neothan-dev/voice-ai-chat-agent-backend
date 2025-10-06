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
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import sqlite3
from loguru import logger

# 配置
LOG_DATABASE_PATH = "logs/ai_interactions.db"
LOG_FILE_PATH = "logs/ai_interactions.log"
ENABLE_DATABASE_LOGGING = True
ENABLE_FILE_LOGGING = True

# 确保日志目录存在
os.makedirs("logs", exist_ok=True)

def log_interaction(session_id: Optional[str], user_id: Optional[str], 
                   text: str, reply: str, emotion: str, intent_id: int, 
                   confidence: float, explain: str, language: str = "zh") -> str:
    """
    记录AI交互日志（支持多语言）
    Args:
        session_id: 会话ID
        user_id: 用户ID
        text: 用户输入文本
        reply: AI回复
        emotion: 检测的情感
        intent: 识别的意图
        confidence: 置信度
        explain: 解释文本
        language: 交互语言
    Returns:
        日志ID
    """
    try:
        # 生成日志ID
        log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # 构建日志数据
        log_data = {
            "log_id": log_id,
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "user_input": text,
            "ai_reply": reply,
            "emotion": emotion,
            "intent_id": intent_id,
            "confidence": confidence,
            "explanation": explain,
            "processing_time": 0.0,  # 可以添加实际处理时间
            "model_used": "voice_ai_chat_model",
            "language": language
        }
        
        # 记录到数据库
        if ENABLE_DATABASE_LOGGING:
            _log_to_database(log_data)
        
        # 记录到文件
        if ENABLE_FILE_LOGGING:
            _log_to_file(log_data)
        
        # 控制台输出
        logger.info(f"AI交互记录: {log_id}")
        
        return log_id
        
    except Exception as e:
        logger.error(f"日志记录失败: {e}")
        return ""

def _log_to_database(log_data: Dict[str, Any]) -> None:
    """记录到数据库"""
    try:
        conn = sqlite3.connect(LOG_DATABASE_PATH)
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_interactions (
                log_id TEXT PRIMARY KEY,
                session_id TEXT,
                user_id TEXT,
                timestamp TEXT,
                user_input TEXT,
                ai_reply TEXT,
                emotion TEXT,
                intent_id INTEGER,
                confidence REAL,
                explanation TEXT,
                processing_time REAL,
                model_used TEXT,
                language TEXT
            )
        ''')
        
        # 插入数据
        cursor.execute('''
            INSERT INTO ai_interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_data["log_id"],
            log_data["session_id"],
            log_data["user_id"],
            log_data["timestamp"],
            log_data["user_input"],
            log_data["ai_reply"],
            log_data["emotion"],
            log_data["intent_id"],
            log_data["confidence"],
            log_data["explanation"],
            log_data["processing_time"],
            log_data["model_used"],
            log_data["language"]
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"数据库日志记录失败: {e}")

def _log_to_file(log_data: Dict[str, Any]) -> None:
    """记录到文件"""
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
            
    except Exception as e:
        logger.error(f"文件日志记录失败: {e}")

def _detect_language(text: str) -> str:
    """检测语言"""
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        return "zh"
    else:
        return "en"

def log_system_event(event_type: str, event_data: Dict[str, Any], 
                    severity: str = "info") -> str:
    """
    记录系统事件
    Args:
        event_type: 事件类型
        event_data: 事件数据
        severity: 严重程度 (debug, info, warning, error)
    Returns:
        事件ID
    """
    try:
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        event_log = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": timestamp,
            "severity": severity,
            "data": event_data
        }
        
        # 记录到文件
        with open("logs/system_events.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(event_log, ensure_ascii=False) + "\n")
        
        # 控制台输出
        if severity == "error":
            logger.error(f"系统事件: {event_type} - {event_data}")
        elif severity == "warning":
            logger.warning(f"系统事件: {event_type} - {event_data}")
        else:
            logger.info(f"系统事件: {event_type} - {event_data}")
        
        return event_id
        
    except Exception as e:
        logger.error(f"系统事件记录失败: {e}")
        return ""

def log_error(error_type: str, error_message: str, 
             stack_trace: Optional[str] = None, 
             context: Optional[Dict[str, Any]] = None) -> str:
    """
    记录错误日志
    Args:
        error_type: 错误类型
        error_message: 错误消息
        stack_trace: 堆栈跟踪
        context: 上下文信息
    Returns:
        错误ID
    """
    try:
        error_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        error_log = {
            "error_id": error_id,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": timestamp,
            "stack_trace": stack_trace,
            "context": context or {}
        }
        
        # 记录到文件
        with open("logs/errors.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(error_log, ensure_ascii=False) + "\n")
        
        # 控制台输出
        logger.error(f"错误: {error_type} - {error_message}")
        
        return error_id
        
    except Exception as e:
        logger.error(f"错误日志记录失败: {e}")
        return ""

def get_interaction_history(user_id: Optional[str] = None, 
                          session_id: Optional[str] = None, 
                          limit: int = 100) -> List[Dict[str, Any]]:
    """
    获取交互历史
    Args:
        user_id: 用户ID
        session_id: 会话ID
        limit: 限制数量
    Returns:
        交互历史列表
    """
    try:
        if not ENABLE_DATABASE_LOGGING:
            return []
        
        conn = sqlite3.connect(LOG_DATABASE_PATH)
        cursor = conn.cursor()
        
        query = "SELECT * FROM ai_interactions WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 转换为字典列表
        columns = [description[0] for description in cursor.description]
        history = []
        
        for row in rows:
            history.append(dict(zip(columns, row)))
        
        conn.close()
        return history
        
    except Exception as e:
        logger.error(f"获取交互历史失败: {e}")
        return []

def get_statistics(days: int = 30) -> Dict[str, Any]:
    """
    获取统计信息
    Args:
        days: 统计天数
    Returns:
        统计信息
    """
    try:
        if not ENABLE_DATABASE_LOGGING:
            return {}
        
        conn = sqlite3.connect(LOG_DATABASE_PATH)
        cursor = conn.cursor()
        
        # 计算时间范围
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_date = from_date.replace(day=from_date.day - days)
        from_date_str = from_date.isoformat()
        
        # 总交互数
        cursor.execute(
            "SELECT COUNT(*) FROM ai_interactions WHERE timestamp >= ?",
            (from_date_str,)
        )
        total_interactions = cursor.fetchone()[0]
        
        # 意图分布
        cursor.execute(
            "SELECT intent, COUNT(*) FROM ai_interactions WHERE timestamp >= ? GROUP BY intent",
            (from_date_str,)
        )
        intent_distribution = dict(cursor.fetchall())
        
        # 情感分布
        cursor.execute(
            "SELECT emotion, COUNT(*) FROM ai_interactions WHERE timestamp >= ? GROUP BY emotion",
            (from_date_str,)
        )
        emotion_distribution = dict(cursor.fetchall())
        
        # 语言分布
        cursor.execute(
            "SELECT language, COUNT(*) FROM ai_interactions WHERE timestamp >= ? GROUP BY language",
            (from_date_str,)
        )
        language_distribution = dict(cursor.fetchall())
        
        # 平均置信度
        cursor.execute(
            "SELECT AVG(confidence) FROM ai_interactions WHERE timestamp >= ?",
            (from_date_str,)
        )
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_interactions": total_interactions,
            "intent_distribution": intent_distribution,
            "emotion_distribution": emotion_distribution,
            "language_distribution": language_distribution,
            "average_confidence": avg_confidence,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return {}

def cleanup_old_logs(days_to_keep: int = 90) -> int:
    """
    清理旧日志
    Args:
        days_to_keep: 保留天数
    Returns:
        删除的记录数
    """
    try:
        if not ENABLE_DATABASE_LOGGING:
            return 0
        
        conn = sqlite3.connect(LOG_DATABASE_PATH)
        cursor = conn.cursor()
        
        # 计算删除时间点
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
        cutoff_date_str = cutoff_date.isoformat()
        
        # 删除旧记录
        cursor.execute(
            "DELETE FROM ai_interactions WHERE timestamp < ?",
            (cutoff_date_str,)
        )
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"清理了 {deleted_count} 条旧日志记录")
        return deleted_count
        
    except Exception as e:
        logger.error(f"清理旧日志失败: {e}")
        return 0

def export_logs_to_json(file_path: str, 
                       user_id: Optional[str] = None,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> bool:
    """
    导出日志到JSON文件
    Args:
        file_path: 导出文件路径
        user_id: 用户ID过滤
        start_date: 开始日期
        end_date: 结束日期
    Returns:
        是否成功
    """
    try:
        if not ENABLE_DATABASE_LOGGING:
            return False
        
        conn = sqlite3.connect(LOG_DATABASE_PATH)
        cursor = conn.cursor()
        
        query = "SELECT * FROM ai_interactions WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 转换为字典列表
        columns = [description[0] for description in cursor.description]
        logs = []
        
        for row in rows:
            logs.append(dict(zip(columns, row)))
        
        conn.close()
        
        # 写入JSON文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功导出 {len(logs)} 条日志到 {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"导出日志失败: {e}")
        return False 