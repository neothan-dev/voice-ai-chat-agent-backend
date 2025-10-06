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

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import base64
from starlette.websockets import WebSocketState
from services.ai_comprehensive_service import ai_comprehensive_service_stream
from services.nlp_service import get_ai_response
from api.auth import get_current_user
from models.user import User
import asyncio
from services.translation_service import translate_text

router = APIRouter(prefix="/ai", tags=["ai"])

class AIRequest(BaseModel):
    input: str

@router.post("/response")
def ai_response(data: AIRequest, current_user: User = Depends(get_current_user)):
    """AI对话接口 - 需要用户认证（支持会话管理）"""
    from services.session_service import session_manager
    
    # 创建新会话（不设置默认语言，等待动态检测）
    session_id = session_manager.create_session(
        user_id=current_user.id
    )
    
    print(f"用户 {current_user.username} 使用会话: {session_id}")
    reply, intent_id, confidence = get_ai_response(data.input, "zh", session_id, current_user.id)
    print("reply ->", reply)
    
    return {
        "response": f"{reply}",
        "session_id": session_id,
        "intent_id": intent_id,
        "confidence": confidence
    }

@router.get("/personalized-advice")
def get_personalized_advice(current_user: User = Depends(get_current_user)):
    """获取用户个性化AI建议 - 需要用户认证"""
    # 根据用户信息生成个性化建议
    user_age = current_user.age or 25
    user_region = current_user.region or "未知"
    
    # 根据用户年龄和地区生成建议
    if user_age < 30:
        advice = f"作为{user_age}岁的年轻人，建议您：\n1. 保持规律作息\n2. 多进行户外运动\n3. 注意营养均衡"
    elif user_age < 50:
        advice = f"作为{user_age}岁的中年人，建议您：\n1. 定期体检\n2. 适量运动\n3. 控制饮食"
    else:
        advice = f"作为{user_age}岁的年长者，建议您：\n1. 保持适度活动\n2. 定期健康检查\n3. 注意保暖"
    
    return {"advice": advice}

# 会话管理相关API
class SessionRequest(BaseModel):
    session_id: Optional[str] = None
    voice_style: Optional[str] = None

@router.post("/session/create")
def create_session(data: SessionRequest, current_user: User = Depends(get_current_user)):
    """创建新的AI会话（语言将动态检测）"""
    from services.session_service import session_manager
    
    session_id = session_manager.create_session(
        user_id=current_user.id,
        voice_style=data.voice_style
    )
    
    return {
        "session_id": session_id,
        "user_id": current_user.id,
        "voice_style": data.voice_style,
        "language": "动态检测中"
    }

@router.get("/session/{session_id}")
def get_session_info(session_id: str, current_user: User = Depends(get_current_user)):
    """获取会话信息"""
    from services.session_service import session_manager
    
    session = session_manager.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "is_active": session.is_active,
        "language": session.language,
        "voice_style": session.voice_style,
        "conversation_count": session.conversation_count,
        "context_summary": session.context_summary
    }

@router.get("/session/{session_id}/history")
def get_session_history(session_id: str, limit: int = 10, current_user: User = Depends(get_current_user)):
    """获取会话历史"""
    from services.session_service import session_manager
    
    session = session_manager.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    
    history = session_manager.get_conversation_history(session_id, limit)
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": msg.id,
                "type": msg.message_type,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "intent_id": msg.intent_id,
                "confidence": msg.confidence,
                "emotion": msg.emotion,
                "language": msg.language
            }
            for msg in history
        ]
    }

@router.delete("/session/{session_id}")
def close_session(session_id: str, current_user: User = Depends(get_current_user)):
    """关闭会话"""
    from services.session_service import session_manager
    
    session = session_manager.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    
    success = session_manager.close_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="关闭会话失败")
    
    return {"message": "会话已关闭"}

@router.get("/session/{session_id}/statistics")
def get_session_statistics(session_id: str, current_user: User = Depends(get_current_user)):
    """获取会话统计信息"""
    from services.session_service import session_manager
    
    session = session_manager.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话不存在或无权限访问")
    
    stats = session_manager.get_session_statistics(session_id)
    return stats

@router.get("/sessions/active")
def get_user_active_sessions(current_user: User = Depends(get_current_user)):
    """获取用户的活跃会话列表"""
    from services.session_service import session_manager
    
    sessions = session_manager.get_user_active_sessions(current_user.id)
    
    return {
        "user_id": current_user.id,
        "sessions": [
            {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "language": session.language,
                "voice_style": session.voice_style,
                "conversation_count": session.conversation_count,
                "context_summary": session.context_summary
            }
            for session in sessions
        ]
    }

@router.websocket("/voice_chat")
async def voice_chat(websocket: WebSocket):
    await websocket.accept()
    
    # 获取用户认证信息
    user = None
    try:
        # 从查询参数获取token
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="缺少认证Token")
            return
        
        # 验证token并获取用户信息
        from api.auth import verify_token
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=4001, reason="无效的Token")
            return
        
        # 获取用户信息
        from sqlmodel import Session, select
        from core.db import engine
        with Session(engine) as session:
            user = session.exec(select(User).where(User.id == user_id)).first()
            if not user:
                await websocket.close(code=4001, reason="用户不存在")
                return
        
        print(f"用户 {user.username} 连接语音聊天")
        
    except Exception as e:
        print(f"WebSocket认证失败: {e}")
        await websocket.close(code=4001, reason="认证失败")
        return
    
    # 初始化会话管理
    from services.session_service import session_manager
    
    # 创建新会话（不设置默认语言，等待动态检测）
    session_id = session_manager.create_session(
        user_id=user.id
    )
    
    user_id = user.id
    audio_buffer = []
    voice_style = None  # 用户选择的音色
    
    print(f"用户 {user.username} 开始语音聊天，会话ID: {session_id}")
    
    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            message = await websocket.receive()
            if "bytes" in message:
                audio_chunk = message["bytes"]
                audio_buffer.append(audio_chunk)
                print(f"用户 {user.username} 音频数据: {len(audio_chunk)} bytes")
                # 可选：实时处理
            elif "text" in message:
                text = message["text"]
                try:
                    data = json.loads(text)
                    
                    # 处理音色信息
                    if data.get("type") == "voice_style":
                        voice_style = data.get("voice_style")
                        print(f"用户 {user.username} 选择音色: {voice_style}")
                        continue
                    
                    if data.get("end_of_utterance") is True:
                        if data.get("ignore_flag") is True:
                            print(f"用户 {user.username} 【IGNORE SENTENCE】low_volume_ignored_sentence")
                            audio_buffer = [] 
                            continue
                        
                        audio_chunk = b''.join(audio_buffer)
                        print(f"用户 {user.username} 处理音频: {len(audio_chunk)} bytes")
                        audio_buffer = [] 
                        
                        # 获取当前页面信息
                        current_page = data.get("current_page", {})
                        print(f"用户 {user.username} 当前页面信息: {current_page}")
                        
                        # AI处理（流式版本）
                        print(f"用户 {user.username} 开始流式AI处理")
                        
                        # 使用流式服务
                        async for result in ai_comprehensive_service_stream(
                            audio_chunk, 
                            session_id, 
                            user_id,
                            voice_style,  # 传递音色信息
                            current_page  # 传递当前页面信息
                        ):
                            if result['type'] == 'audio_segment':
                                # 处理音频段
                                audio_base64 = base64.b64encode(result['audio']).decode('utf-8')
                                await websocket.send_json({
                                    "type": "audio_segment",
                                    "index": result['index'],
                                    "total": result['total'],
                                    "text": result['text'],
                                    "base64audio": audio_base64,
                                    "method": result['method']
                                })
                                print(f"用户 {user.username} 发送音频段 {result['index'] + 1}/{result['total']}")
                                
                            elif result['type'] == 'final_result':
                                # 处理最终结果
                                await websocket.send_json({
                                    "type": "conclution",
                                    "emotion": translate_text(result['emotion'], "zh", result['user_lang']),
                                    "intent": translate_text(result['intent'], "zh", result['user_lang']),
                                    "confidence": result['confidence'],
                                    "explain": result['explain'],
                                    "navigation": result['navigation'],
                                    "user_id": user_id,
                                    "username": user.username
                                })
                                print(f"用户 {user.username} AI响应完成: intent={result['intent']}, emotion={result['emotion']}")
                except json.JSONDecodeError:
                    print(f"用户 {user.username} Invalid JSON format")
    except WebSocketDisconnect:
        print(f"用户 {user.username} 断开语音聊天连接")
        # 关闭会话
        session_manager.close_session(session_id)
    except Exception as e:
        print(f"用户 {user.username} 语音聊天错误: {e}")
        # 关闭会话
        session_manager.close_session(session_id)
    finally:
        print(f"用户 {user.username} 语音聊天会话结束")
        # 确保会话被关闭
        try:
            session_manager.close_session(session_id)
        except:
            pass 