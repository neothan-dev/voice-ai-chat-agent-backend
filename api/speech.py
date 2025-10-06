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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import base64
from services.stt_service import stt_stream, detect_language_from_audio
from services.tts_service import tts_stream, EMOTION_VOICE_PARAMS
from services.translation_service import detect_language
from models.user import User
from api.auth import get_current_user
import os

router = APIRouter(prefix="/speech", tags=["speech"])

class STTRequest(BaseModel):
    audio: str  # base64编码音频

class TTSRequest(BaseModel):
    text: str
    lang: str = None
    emotion: str = "中性"  # 支持情感参数：开心、悲伤、愤怒、焦虑、平静、中性
    voice_style: str = None  # 支持音色参数：音色ID（如：xiaoxiao, yunxi, yunyang, xiaoyi, yunfeng）

DEFAULT_STT_LANG = os.getenv("DEFAULT_STT_LANG", "zh")
@router.post("/stt")
def speech_to_text(data: STTRequest, current_user: User = Depends(get_current_user)):
    """语音转文本 - 需要用户认证"""
    audio_bytes = base64.b64decode(data.audio)
    detected_lang = detect_language_from_audio(audio_bytes) or DEFAULT_STT_LANG
    succ, text, lang, _method = stt_stream(audio_bytes)
    print(f"用户 {current_user.username} 语音转文本: {text}")
    return {"text": text, "lang": lang or detected_lang}

DEFAULT_TTS_LANG = os.getenv("DEFAULT_TTS_LANG", "zh")
@router.post("/tts")
def text_to_speech(data: TTSRequest, current_user: User = Depends(get_current_user)):
    """文本转语音 - 需要用户认证，支持多语言音色"""
    lang = data.lang or detect_language(data.text) or DEFAULT_TTS_LANG
    emotion = getattr(data, 'emotion', '中性')  # 支持情感参数
    voice_style = getattr(data, 'voice_style', None)  # 支持音色参数
    
    # 使用多语言音色服务
    if voice_style:
        from services.voice_style_service import get_voice_for_language_and_style
        language_specific_voice = get_voice_for_language_and_style(voice_style, lang)
        print(f"用户 {current_user.username} 使用音色 {voice_style} 语言 {lang} -> 语音 {language_specific_voice}")
    
    # 传递音色参数到TTS服务
    audio_bytes, _method = tts_stream(data.text, lang, emotion, voice_style)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    print(f"用户 {current_user.username} 文本转语音: {data.text[:50]}... (情感: {emotion}, 音色: {voice_style}, 语言: {lang})")
    return {"audio": audio_b64, "lang": lang, "emotion": emotion, "voice_style": voice_style}

@router.get("/preferences")
def get_voice_preferences(current_user: User = Depends(get_current_user)):
    """获取用户语音偏好设置 - 需要用户认证"""
    # TODO: 从数据库获取用户语音偏好
    preferences = {
        "default_language": "zh",
        "voice_speed": 1.0,
        "voice_pitch": 1.0,
        "auto_play": True,
        "voice_type": "female",
    }
    return preferences

@router.put("/preferences")
def update_voice_preferences(preferences: dict, current_user: User = Depends(get_current_user)):
    """更新用户语音偏好设置 - 需要用户认证"""
    # TODO: 将用户语音偏好保存到数据库
    print(f"用户 {current_user.username} 更新语音偏好: {preferences}")
    return {"message": "偏好设置更新成功", "preferences": preferences}

@router.get("/emotions")
def get_available_emotions():
    """获取可用的情感类型"""
    emotions = [
        {"id": "开心", "name": "开心", "description": "愉快、兴奋的情感"},
        {"id": "悲伤", "name": "悲伤", "description": "难过、沮丧的情感"},
        {"id": "愤怒", "name": "愤怒", "description": "生气、恼火的情感"},
        {"id": "焦虑", "name": "焦虑", "description": "担心、紧张的情感"},
        {"id": "平静", "name": "平静", "description": "冷静、放松的情感"},
        {"id": "中性", "name": "中性", "description": "正常、平和的情感"}
    ]
    return {"emotions": emotions} 

@router.get("/voice-styles")
def get_voice_styles(current_user: User = Depends(get_current_user)):
    """获取可用的音色风格列表"""
    from services.voice_style_service import get_available_voice_styles
    styles = get_available_voice_styles()
    return {"voice_styles": styles}

@router.get("/voice-styles/{voice_style_id}")
def get_voice_style_info(voice_style_id: str, current_user: User = Depends(get_current_user)):
    """获取指定音色风格的详细信息"""
    from services.voice_style_service import get_voice_style_info
    style_info = get_voice_style_info(voice_style_id)
    if style_info:
        return style_info
    else:
        raise HTTPException(status_code=404, detail="音色风格不存在")

@router.get("/voice-styles/{voice_style_id}/preview")
def get_voice_style_preview(
    voice_style_id: str, 
    language: str = "zh",
    current_user: User = Depends(get_current_user)
):
    """获取音色风格预览信息"""
    from services.voice_style_service import get_voice_style_preview
    preview = get_voice_style_preview(voice_style_id, language)
    return preview

@router.get("/voice-styles/{voice_style_id}/languages")
def get_supported_languages_for_style(
    voice_style_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取音色风格支持的语言列表"""
    from services.voice_style_service import get_supported_languages_for_style
    languages = get_supported_languages_for_style(voice_style_id)
    return {"voice_style": voice_style_id, "supported_languages": languages} 