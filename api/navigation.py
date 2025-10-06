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

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.navigation_service import navigation_service
from loguru import logger

router = APIRouter(prefix="/navigation", tags=["navigation"])

class NavigationRequest(BaseModel):
    text: str
    lang: str = "zh"

class NavigationResponse(BaseModel):
    type: str
    action: Optional[str]
    target: Optional[str]
    route: Optional[str]
    name: Optional[str]
    confidence: float
    message: str
    parameters: Optional[Dict[str, Any]] = None

@router.get("/pages", response_model=List[Dict[str, Any]])
async def get_available_pages():
    """获取所有可用页面"""
    try:
        pages = navigation_service.get_available_pages()
        return pages
    except Exception as e:
        logger.error(f"获取页面列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取页面列表失败")

@router.get("/pages/{route}")
async def get_page_by_route(route: str):
    """根据路由获取页面信息"""
    try:
        page = navigation_service.get_page_by_route(route)
        if not page:
            raise HTTPException(status_code=404, detail="页面不存在")
        return page
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取页面信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取页面信息失败")

@router.post("/detect", response_model=NavigationResponse)
async def detect_navigation_intent(request: NavigationRequest):
    """检测导航意图"""
    try:
        result = navigation_service.detect_navigation_intent(request.text, request.lang)
        return NavigationResponse(**result)
    except Exception as e:
        logger.error(f"导航意图检测失败: {e}")
        raise HTTPException(status_code=500, detail="导航意图检测失败")

@router.post("/reload")
async def reload_navigation_configs():
    """重新加载导航配置"""
    try:
        navigation_service.reload_configs()
        return {"message": "导航配置已重新加载"}
    except Exception as e:
        logger.error(f"重新加载导航配置失败: {e}")
        raise HTTPException(status_code=500, detail="重新加载导航配置失败") 