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

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlmodel import Session, select
from models.user import User
from core.db import engine
from passlib.context import CryptContext
import jwt
import json


router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
from core.config import SECRET_KEY
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str = ""
    email: Optional[str] = None
    age: int = 0
    region: str = ""

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    age: Optional[int] = None
    region: Optional[str] = None
    preferences: Optional[dict] = None

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7天过期
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的Token")

def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证Token")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的Token")
    
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user

def user_to_response(user: User) -> dict:
    """将User对象转换为API响应格式"""
    import json
    
    # 解析preferences JSON字符串
    preferences = None
    if user.preferences:
        try:
            preferences = json.loads(user.preferences)
        except (json.JSONDecodeError, TypeError):
            preferences = None
    
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "age": user.age,
        "region": user.region,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "preferences": preferences,
    }

@router.post("/register")
def register(data: RegisterRequest):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == data.username)).first()
        if user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        user = User(
            username=data.username,
            password_hash=pwd_context.hash(data.password),
            full_name=data.full_name,
            email=data.email,
            age=data.age if data.age > 0 else None,
            region=data.region if data.region else None,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # 创建访问令牌
        access_token = create_access_token({"sub": user.id})
        
        return {
            "message": "注册成功",
            "user": user_to_response(user),
            "token": access_token
        }

@router.post("/login")
def login(data: LoginRequest):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == data.username)).first()
        if not user or not pwd_context.verify(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # 创建访问令牌
        access_token = create_access_token({"sub": user.id})
        
        return {
            "user": user_to_response(user),
            "token": access_token
        }

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return user_to_response(current_user)

@router.put("/profile")
def update_profile(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == current_user.id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新用户信息
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.email is not None:
            user.email = data.email
        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url
        if data.age is not None:
            user.age = data.age
        if data.region is not None:
            user.region = data.region
        if data.preferences is not None:
            import json
            user.preferences = json.dumps(data.preferences)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user_to_response(user)

@router.put("/change-password")
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user)
):
    """修改密码"""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == current_user.id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 验证旧密码
        if not pwd_context.verify(data.old_password, user.password_hash):
            raise HTTPException(status_code=400, detail="旧密码错误")
        
        # 更新密码
        user.password_hash = pwd_context.hash(data.new_password)
        session.add(user)
        session.commit()
        
        return {"message": "密码修改成功"}

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，可以将token加入黑名单
    return {"message": "登出成功"}

@router.get("/preferences")
def get_preferences(current_user: User = Depends(get_current_user)):
    """获取用户偏好设置"""
    import json
    
    preferences = None
    if current_user.preferences:
        try:
            preferences = json.loads(current_user.preferences)
        except (json.JSONDecodeError, TypeError):
            preferences = {}
    
    return {"preferences": preferences or {}}

@router.put("/preferences")
def update_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user)
):
    """更新用户偏好设置"""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == current_user.id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        import json
        user.preferences = json.dumps(preferences)
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # 返回解析后的preferences以保持一致性
        try:
            parsed_preferences = json.loads(user.preferences)
        except (json.JSONDecodeError, TypeError):
            parsed_preferences = {}
        
        return {"preferences": parsed_preferences} 