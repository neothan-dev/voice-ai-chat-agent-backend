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
import struct
import math
import tempfile
import base64
from typing import Optional, Tuple
import requests
from loguru import logger

# 配置
from core.config import OPENAI_API_KEY, AZURE_SPEECH_KEY, DEFAULT_TTS_REGION, DEFAULT_TTS_LANG

# TTS方案选择：'rest_api' 或 'sdk'
# REST API方案：兼容Docker环境，推荐使用
# SDK方案：功能更丰富，但在Docker中可能不兼容
AZURE_TTS_METHOD = 'rest_api'  # 可选: 'rest_api' 或 'sdk'

# 导入多语言音色服务
from services.voice_style_service import get_voice_for_language_and_style, update_emotion_voice_params_for_style

# 语音参数
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_BITS_PER_SAMPLE = 16
DEFAULT_CHANNELS = 1

# 情感语音参数映射（同一说话人，不同语调）
EMOTION_VOICE_PARAMS = {
    "开心": {
        "rate": 1.2,      # 语速稍快
        "pitch": 1.1,     # 音调稍高
        "volume": 1.1,    # 音量稍大
        "voice": "alloy", # OpenAI声音
        "azure_voice": "zh-CN-XiaoxiaoNeural",  # 统一使用小晓音色
        "style": "cheerful"
    },
    "悲伤": {
        "rate": 0.8,      # 语速较慢
        "pitch": 0.9,     # 音调较低
        "volume": 0.9,    # 音量较小
        "voice": "alloy",
        "azure_voice": "zh-CN-XiaoxiaoNeural",  # 统一使用小晓音色
        "style": "sad"
    },
    "愤怒": {
        "rate": 1.3,      # 语速快
        "pitch": 1.2,     # 音调高
        "volume": 1.3,    # 音量大
        "voice": "alloy",
        "azure_voice": "zh-CN-XiaoxiaoNeural",  # 统一使用小晓音色
        "style": "angry"
    },
    "焦虑": {
        "rate": 1.1,      # 语速稍快
        "pitch": 1.05,    # 音调稍高
        "volume": 1.0,    # 正常音量
        "voice": "alloy",
        "azure_voice": "zh-CN-XiaoxiaoNeural",  # 统一使用小晓音色
        "style": "worried"
    },
    "平静": {
        "rate": 0.9,      # 语速较慢
        "pitch": 1.0,     # 正常音调
        "volume": 0.95,   # 音量稍小
        "voice": "alloy",
        "azure_voice": "zh-CN-XiaoxiaoNeural",  # 统一使用小晓音色
        "style": "calm"
    },
    "中性": {
        "rate": 1.0,      # 正常语速
        "pitch": 1.0,     # 正常音调
        "volume": 1.0,    # 正常音量
        "voice": "alloy",
        "azure_voice": "zh-CN-XiaoxiaoNeural",  # 统一使用小晓音色
        "style": "neutral"
    }
}

def tts_stream(text: str, lang: str, emotion: str = "中性", voice_style: str = None) -> Tuple[bytes, str]:
    """
    文本转语音服务（支持情感和多语言音色）
    Args:
        text: 要转换的文本
        lang: 语言代码
        emotion: 情感类型（开心、悲伤、愤怒、焦虑、平静、中性）
        voice_style: 音色风格（xiaoxiao, yunxi, yunyang, xiaoyi, default）
    Returns:
        音频数据字节流
    """
    try:
        # 获取情感语音参数
        voice_params = EMOTION_VOICE_PARAMS.get(emotion, EMOTION_VOICE_PARAMS["中性"])
        
        # 如果指定了音色，根据语言获取对应的语音
        if voice_style:
            # 验证音色ID是否有效
            from services.voice_style_service import validate_voice_style_id, get_voice_style_name
            if not validate_voice_style_id(voice_style):
                logger.warning(f"无效的音色ID: {voice_style}，使用默认音色")
                voice_style = "default"
            
            # 获取对应语言的语音
            language_specific_voice = get_voice_for_language_and_style(voice_style, lang)
            logger.info(f"使用音色 {voice_style} ({get_voice_style_name(voice_style)}) 语言 {lang} -> 语音 {language_specific_voice}")
            
            # 更新语音参数
            voice_params = voice_params.copy()
            voice_params['azure_voice'] = language_specific_voice
        
        # 尝试使用不同的TTS服务
        if AZURE_TTS_METHOD == 'sdk':
            # 使用SDK方案（备用）
            audio_data = _try_azure_tts_sdk_with_emotion(text, lang, voice_params)
        else:
            # 使用REST API方案（推荐）
            audio_data = _try_azure_tts_with_emotion(text, lang, voice_params)
            
        if audio_data:
            return audio_data, "azure"
        else:
            print("【API Service Failed!】Azure文本转语音失败!")

        audio_data = _try_openai_tts_with_emotion(text, lang, voice_params)
        if audio_data:
            return audio_data, "openai"
        else:
            print("【API Service Failed!】openai文本转语音失败!")
            
        audio_data = _try_google_tts_with_emotion(text, lang, voice_params)
        if audio_data:
            return audio_data, "google"
        else:
            print("【API Service Failed!】Google文本转语音失败!")
            
        # 使用本地TTS生成
        return _local_tts_generation_with_emotion(text, lang, voice_params), "local"
        
    except Exception as e:
        logger.error(f"TTS处理失败: {e}")
        return _generate_fallback_audio(text, lang), "fallback"

def _try_openai_tts_with_emotion(text: str, lang: str, voice_params: dict) -> Optional[bytes]:
    """尝试使用OpenAI TTS API（支持情感）"""
    if not OPENAI_API_KEY:
        return None
    
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # 选择合适的声音
        voice = voice_params.get("voice", _get_voice_for_language(lang))
        
        # 构建带情感的SSML文本
        ssml_text = _build_emotion_ssml(text, voice_params)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=ssml_text,
            response_format="mp3"
        )
        
        # 获取音频数据
        audio_data = response.content
        
        # 转换为WAV格式（如果需要）
        if not audio_data.startswith(b'RIFF'):
            audio_data = _convert_to_wav(audio_data)
        
        return audio_data
        
    except Exception as e:
        logger.warning(f"OpenAI TTS失败: {e}")
        return None

def _try_azure_tts_with_emotion(text: str, lang: str, voice_params: dict) -> Optional[bytes]:
    """尝试使用Azure Speech Services TTS REST API（支持情感）"""
    if not AZURE_SPEECH_KEY:
        return None
    
    try:
        # 设置语音参数
        voice_name = voice_params.get("azure_voice", _get_azure_voice_for_language(lang))
        
        # 构建带情感的SSML文本
        ssml_text = _build_azure_emotion_ssml(text, voice_params, voice_name)
        
        # 使用Azure Speech REST API
        return _azure_tts_rest_api(ssml_text, AZURE_SPEECH_KEY, DEFAULT_TTS_REGION)
        
    except Exception as e:
        logger.warning(f"Azure TTS REST API失败: {e}")
        return None

def _try_azure_tts_sdk_with_emotion(text: str, lang: str, voice_params: dict) -> Optional[bytes]:
    """备用方案：使用Azure Speech Services SDK（支持情感）- 在Docker环境中可能不兼容"""
    if not AZURE_SPEECH_KEY:
        return None
    
    try:
        import azure.cognitiveservices.speech as speechsdk
        
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY, 
            region=DEFAULT_TTS_REGION
        )
        
        # 设置语音参数
        voice_name = voice_params.get("azure_voice", _get_azure_voice_for_language(lang))
        speech_config.speech_synthesis_voice_name = voice_name
        
        # 构建带情感的SSML文本
        ssml_text = _build_azure_emotion_ssml(text, voice_params, voice_name)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio_config = speechsdk.AudioConfig(filename=temp_file.name)
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, 
                audio_config=audio_config
            )
            
            result = synthesizer.speak_ssml_async(ssml_text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # 读取生成的音频文件
                with open(temp_file.name, "rb") as f:
                    audio_data = f.read()
                
                # 清理临时文件
                os.unlink(temp_file.name)
                return audio_data
        
        return None
        
    except Exception as e:
        logger.warning(f"Azure TTS SDK失败: {e}")
        return None

def _azure_tts_rest_api(ssml_text: str, speech_key: str, region: str) -> Optional[bytes]:
    """使用Azure Speech REST API进行TTS转换"""
    try:
        endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": speech_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm"
        }
        
        response = requests.post(endpoint, headers=headers, data=ssml_text.encode("utf-8"))
        response.raise_for_status()
        
        # 检查响应内容类型
        content_type = response.headers.get('content-type', '')
        if 'audio' in content_type or response.content.startswith(b'RIFF'):
            return response.content
        else:
            logger.warning(f"Azure TTS REST API返回非音频内容: {content_type}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Azure TTS REST API请求失败: {e}")
        return None
    except Exception as e:
        logger.warning(f"Azure TTS REST API处理失败: {e}")
        return None

def _try_google_tts_with_emotion(text: str, lang: str, voice_params: dict) -> Optional[bytes]:
    """尝试使用Google Cloud Text-to-Speech（支持情感）"""
    try:
        from google.cloud import texttospeech
        
        client = texttospeech.TextToSpeechClient()
        
        # 构建带情感的SSML文本
        ssml_text = _build_google_emotion_ssml(text, voice_params)
        
        # 设置语音参数
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=_get_google_language_code(lang),
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=DEFAULT_SAMPLE_RATE
        )
        
        response = client.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )
        
        return response.audio_content
        
    except Exception as e:
        logger.warning(f"Google TTS失败: {e}")
        return None

def _build_emotion_ssml(text: str, voice_params: dict) -> str:
    """构建带情感的SSML文本（OpenAI格式）"""
    rate = voice_params.get("rate", 1.0)
    pitch = voice_params.get("pitch", 1.0)
    
    # OpenAI TTS不支持复杂的SSML，使用简单的速率调整
    if rate != 1.0:
        return f'<speak rate="{rate}">{text}</speak>'
    else:
        return text

def _build_azure_emotion_ssml(text: str, voice_params: dict, voice_name: str) -> str:
    """构建带情感的SSML文本（Azure格式）"""
    rate = voice_params.get("rate", 1.0)
    pitch = voice_params.get("pitch", 1.0)
    volume = voice_params.get("volume", 1.0)
    style = voice_params.get("style", "neutral")
    
    # Azure Speech Services不支持prosody标签，所有情感都使用express-as或基础SSML
    if style != "neutral":
        # 使用express-as风格
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                 xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
    <voice name="{voice_name}">
        <mstts:express-as style="{style}">
            {text}
        </mstts:express-as>
    </voice>
</speak>'''
    else:
        # 中性情感使用基础SSML，不使用prosody标签
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
    <voice name="{voice_name}">
        {text}
    </voice>
</speak>'''
    
    return ssml

def _build_google_emotion_ssml(text: str, voice_params: dict) -> str:
    """构建带情感的SSML文本（Google格式）"""
    rate = voice_params.get("rate", 1.0)
    pitch = voice_params.get("pitch", 1.0)
    
    # Google TTS的SSML格式
    ssml = f'''<speak>
    <prosody rate="{rate}" pitch="{pitch}">
        {text}
    </prosody>
</speak>'''
    
    return ssml

def _local_tts_generation_with_emotion(text: str, lang: str, voice_params: dict) -> bytes:
    """本地TTS生成（支持情感）"""
    try:
        # 根据文本长度和情感调整音频参数
        text_length = len(text)
        emotion = voice_params.get("style", "neutral")
        
        # 根据情感调整持续时间
        base_duration = 2.0
        if text_length < 10:
            base_duration = 1.0
        elif text_length < 30:
            base_duration = 2.0
        elif text_length < 50:
            base_duration = 3.0
        else:
            base_duration = 4.0
        
        # 根据情感调整持续时间
        emotion_duration_multiplier = {
            "cheerful": 0.9,   # 开心时语速快
            "sad": 1.3,        # 悲伤时语速慢
            "angry": 0.8,      # 愤怒时语速快
            "worried": 1.1,    # 焦虑时语速稍慢
            "calm": 1.2,       # 平静时语速慢
            "neutral": 1.0     # 中性时正常
        }
        
        duration = base_duration * emotion_duration_multiplier.get(emotion, 1.0)
        
        return _generate_speech_like_audio_with_emotion(text, duration, lang, voice_params)
        
    except Exception as e:
        logger.error(f"本地TTS生成失败: {e}")
        return _generate_fallback_audio(text, lang)

def _generate_speech_like_audio_with_emotion(text: str, duration: float, lang: str, voice_params: dict) -> bytes:
    """生成带情感的类似语音的音频"""
    sample_rate = DEFAULT_SAMPLE_RATE
    bits_per_sample = DEFAULT_BITS_PER_SAMPLE
    channels = DEFAULT_CHANNELS
    
    num_samples = int(sample_rate * duration)
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = num_samples * channels * bits_per_sample // 8
    wav_size = 36 + data_size
    
    # WAV文件头
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        wav_size,
        b'WAVE',
        b'fmt ',
        16,  # Subchunk1Size for PCM
        1,   # AudioFormat PCM
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )
    
    # 获取情感参数
    pitch_multiplier = voice_params.get("pitch", 1.0)
    volume_multiplier = voice_params.get("volume", 1.0)
    emotion = voice_params.get("style", "neutral")
    
    # 生成音频数据
    data = []
    for i in range(num_samples):
        # 根据情感调整音频特征
        base_frequency = 200 + (i % 100)
        
        # 根据音调调整频率
        adjusted_frequency = base_frequency * pitch_multiplier
        
        # 根据情感调整振幅
        base_amplitude = 0.3 + 0.2 * math.sin(i / 100)
        
        # 根据情感调整振幅模式
        if emotion == "cheerful":
            amplitude = base_amplitude * volume_multiplier * (1.0 + 0.3 * math.sin(i / 50))
        elif emotion == "sad":
            amplitude = base_amplitude * volume_multiplier * 0.7
        elif emotion == "angry":
            amplitude = base_amplitude * volume_multiplier * (1.0 + 0.5 * math.sin(i / 30))
        elif emotion == "worried":
            amplitude = base_amplitude * volume_multiplier * (0.8 + 0.2 * math.sin(i / 80))
        elif emotion == "calm":
            amplitude = base_amplitude * volume_multiplier * 0.9
        else:  # neutral
            amplitude = base_amplitude * volume_multiplier
        
        value = int(32767 * amplitude * math.sin(2 * math.pi * adjusted_frequency * i / sample_rate))
        data.append(struct.pack('<h', value))
    
    wav_data = b''.join(data)
    return wav_header + wav_data

def _generate_fallback_audio(text: str, lang: str) -> bytes:
    """生成备用音频"""
    # 生成一个简单的提示音
    sample_rate = DEFAULT_SAMPLE_RATE
    bits_per_sample = DEFAULT_BITS_PER_SAMPLE
    channels = DEFAULT_CHANNELS
    duration = 1.0
    
    num_samples = int(sample_rate * duration)
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = num_samples * channels * bits_per_sample // 8
    wav_size = 36 + data_size
    
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        wav_size,
        b'WAVE',
        b'fmt ',
        16,
        1,
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )
    
    # 生成提示音
    beep_samples = int(sample_rate * 0.1)
    data = []
    for i in range(num_samples):
        if i < beep_samples:
            # 440Hz正弦波
            value = int(32767 * 0.5 * math.sin(2 * math.pi * 440 * i / sample_rate))
        else:
            value = 0
        data.append(struct.pack('<h', value))
    
    wav_data = b''.join(data)
    return wav_header + wav_data

def _get_voice_for_language(lang: str) -> str:
    """根据语言获取OpenAI TTS声音"""
    voice_mapping = {
        "zh": "alloy",
        "en": "alloy", 
        "ja": "alloy",
        "ko": "alloy",
        "fr": "alloy",
        "de": "alloy",
        "es": "alloy",
        "ru": "alloy",
        "ar": "alloy",
        "hi": "alloy"
    }
    return voice_mapping.get(lang, "alloy")

def _get_azure_voice_for_language(lang: str) -> str:
    """根据语言获取Azure TTS声音"""
    voice_mapping = {
        "zh": "zh-CN-XiaoxiaoNeural",
        "en": "en-US-JennyNeural",
        "ja": "ja-JP-NanamiNeural",
        "ko": "ko-KR-SunHiNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural",
        "es": "es-ES-ElviraNeural",
        "ru": "ru-RU-SvetlanaNeural",
        "ar": "ar-SA-ZariyahNeural",
        "hi": "hi-IN-SwaraNeural"
    }
    return voice_mapping.get(lang, "zh-CN-XiaoxiaoNeural")

def _get_google_language_code(lang: str) -> str:
    """根据语言获取Google TTS语言代码"""
    language_mapping = {
        "zh": "zh-CN",
        "en": "en-US",
        "ja": "ja-JP",
        "ko": "ko-KR",
        "fr": "fr-FR",
        "de": "de-DE",
        "es": "es-ES",
        "ru": "ru-RU",
        "ar": "ar-SA",
        "hi": "hi-IN"
    }
    return language_mapping.get(lang, "zh-CN")

def _convert_to_wav(audio_data: bytes) -> bytes:
    """将音频数据转换为WAV格式"""
    # 这里可以实现音频格式转换
    # 目前直接返回原数据
    return audio_data

def get_available_voices(lang: str) -> list:
    """获取可用的语音列表"""
    voices = {
        "zh": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-YunyangNeural", "zh-CN-XiaoyiNeural"],
        "en": ["en-US-JennyNeural", "en-US-GuyNeural", "en-GB-SoniaNeural", "en-US-AriaNeural"],
        "ja": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural", "ja-JP-NaokiNeural"],
        "ko": ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural", "ko-KR-YuJinNeural"],
        "fr": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural", "fr-FR-AlainNeural"],
        "de": ["de-DE-KatjaNeural", "de-DE-ConradNeural", "de-DE-AmalaNeural"],
        "es": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural", "es-ES-LaiaNeural"],
        "ru": ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural", "ru-RU-DariyaNeural"],
        "ar": ["ar-SA-ZariyahNeural", "ar-SA-HamedNeural", "ar-SA-SalimNeural"],
        "hi": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural", "hi-IN-AarohiNeural"]
    }
    return voices.get(lang, ["default"])

def adjust_speech_rate(text: str, rate: float = 1.0) -> str:
    """调整语音速率（通过SSML标签）"""
    if rate == 1.0:
        return text
    
    # 使用SSML标签调整速率
    return f'<speak rate="{rate}">{text}</speak>'

def adjust_pitch(text: str, pitch: float = 1.0) -> str:
    """调整音调（通过SSML标签）"""
    if pitch == 1.0:
        return text
    
    return f'<speak pitch="{pitch}">{text}</speak>'