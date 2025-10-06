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
from models.user import User
from api.auth import get_current_user
from datetime import datetime, date
import random

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/steps")
def get_steps_data(current_user: User = Depends(get_current_user)):
    """获取用户步数数据 - 需要用户认证"""
    # 根据用户年龄生成合理的步数数据
    user_age = current_user.age or 25
    
    if user_age < 30:
        base_steps = random.randint(8000, 12000)
        activity = "活跃"
    elif user_age < 50:
        base_steps = random.randint(6000, 10000)
        activity = "中等"
    else:
        base_steps = random.randint(4000, 8000)
        activity = "轻度"
    
    return {
        "steps": base_steps,
        "activity": activity,
        "goal": 10000,
        "progress": (base_steps / 10000) * 100,
        "calories": base_steps * 0.04,
    }

@router.get("/weather")
def get_weather_data(current_user: User = Depends(get_current_user)):
    """获取天气数据 - 需要用户认证"""
    # 根据用户地区返回天气数据
    user_region = current_user.region or "北京"
    
    weather_data = {
        "temp": "25°C",
        "desc": "晴",
        "humidity": "65%",
        "wind": "微风",
        "air_quality": "良好",
        "region": user_region,
    }
    
    return weather_data

@router.get("/sleep")
def get_sleep_data(current_user: User = Depends(get_current_user)):
    """获取睡眠数据 - 需要用户认证"""
    user_age = current_user.age or 25
    
    # 根据年龄生成合理的睡眠数据
    if user_age < 30:
        sleep_hours = random.uniform(7.0, 9.0)
        quality = "良好"
    elif user_age < 50:
        sleep_hours = random.uniform(6.5, 8.5)
        quality = "中等"
    else:
        sleep_hours = random.uniform(6.0, 8.0)
        quality = "一般"
    
    return {
        "hours": round(sleep_hours, 1),
        "quality": quality,
        "deep_sleep": round(sleep_hours * 0.25, 1),
        "rem_sleep": round(sleep_hours * 0.2, 1),
        "goal": 8.0,
    }

@router.get("/body-metrics")
def get_body_metrics_data(current_user: User = Depends(get_current_user)):
    """获取身体指标数据 - 需要用户认证"""
    user_age = current_user.age or 25
    
    # 根据年龄生成合理的身体指标
    if user_age < 30:
        weight = random.randint(55, 75)
        height = random.randint(160, 180)
    elif user_age < 50:
        weight = random.randint(60, 80)
        height = random.randint(160, 180)
    else:
        weight = random.randint(55, 75)
        height = random.randint(155, 175)
    
    bmi = round(weight / ((height / 100) ** 2), 1)
    
    return {
        "weight": weight,
        "height": height,
        "bmi": bmi,
        "bmi_status": "正常" if 18.5 <= bmi <= 24 else "偏重" if bmi > 24 else "偏轻",
        "goal_weight": weight,
    }

@router.get("/recipe")
def get_recipe_data(current_user: User = Depends(get_current_user)):
    """获取食谱建议数据 - 需要用户认证"""
    user_age = current_user.age or 25
    
    # 根据用户年龄和偏好生成食谱建议
    if user_age < 30:
        suggestions = [
            "多吃蛋白质丰富的食物",
            "适量补充维生素C",
            "保持水分摄入",
        ]
    elif user_age < 50:
        suggestions = [
            "控制热量摄入",
            "多吃蔬菜水果",
            "适量运动配合饮食",
        ]
    else:
        suggestions = [
            "清淡饮食为主",
            "多吃高纤维食物",
            "注意钙质补充",
        ]
    
    return {
        "suggestion": suggestions[random.randint(0, len(suggestions) - 1)],
        "daily_calories": 2000,
        "protein_goal": "80g",
        "carbs_goal": "250g",
        "fat_goal": "65g",
    } 