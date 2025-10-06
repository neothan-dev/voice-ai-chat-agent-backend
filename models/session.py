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

from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
import json

class AISession(SQLModel, table=True):
    """AI对话会话模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, unique=True)
    user_id: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    language: Optional[str] = None
    voice_style: Optional[str] = None
    context_summary: Optional[str] = None
    conversation_count: int = Field(default=0)
    total_duration: int = Field(default=0)
    
    session_metadata: Optional[str] = None
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取元数据字典"""
        if self.session_metadata:
            try:
                return json.loads(self.session_metadata)
            except:
                return {}
        return {}
    
    def set_metadata(self, data: Dict[str, Any]) -> None:
        """设置元数据字典"""
        self.session_metadata = json.dumps(data, ensure_ascii=False)
    
    def update_timestamp(self) -> None:
        """更新最后修改时间"""
        self.updated_at = datetime.utcnow()

class ConversationMessage(SQLModel, table=True):
    """对话消息模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    message_type: str = Field(index=True)
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    intent_id: Optional[int] = None
    confidence: Optional[float] = None
    emotion: Optional[str] = None
    language: str = Field(default="zh")
    processing_time: Optional[float] = None
    message_metadata: Optional[str] = None
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取元数据字典"""
        if self.message_metadata:
            try:
                return json.loads(self.message_metadata)
            except:
                return {}
        return {}
    
    def set_metadata(self, data: Dict[str, Any]) -> None:
        """设置元数据字典"""
        self.message_metadata = json.dumps(data, ensure_ascii=False)
